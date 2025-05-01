from flask import Flask, jsonify, render_template
import psutil
import os
import signal
import time
from datetime import datetime
import logging
from statistics import mean

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Health score thresholds
HEALTH_THRESHOLDS = {
    'cpu': {'warning': 70, 'critical': 90},
    'memory': {'warning': 70, 'critical': 90},
    'disk': {'warning': 70, 'critical': 90},
    'temperature': {'warning': 70, 'critical': 85}
}

# Alert history
alert_history = []

# CPU usage cache
last_cpu_usage = None
last_cpu_time = 0
CPU_CACHE_DURATION = 2  # seconds

class SystemStats:
    def __init__(self):
        self.last_cpu_measure_time = 0
        self.last_cpu_value = 0
        self.cpu_values = []
        self.window_size = 3  # Number of samples to average
        self._init_cpu()
    
    def _init_cpu(self):
        """Initialize CPU measurement"""
        try:
            # First call returns 0, so we need multiple calls for initialization
            psutil.cpu_percent(interval=None)
            time.sleep(0.1)
            
            # Take several measurements to initialize the moving average
            for i in range(self.window_size):
                value = psutil.cpu_percent(interval=1.0)  # 1 second interval for initialization
                self.cpu_values.append(value)
                logger.debug(f"Initial CPU measurement {i+1}: {value}%")
            
            self.last_cpu_value = mean(self.cpu_values)
            self.last_cpu_measure_time = time.time()
            logger.debug(f"Initial CPU measurements: {self.cpu_values}, Average: {self.last_cpu_value}%")
        except Exception as e:
            logger.error(f"Error initializing CPU measurements: {str(e)}")
            self.last_cpu_value = 0
            self.cpu_values = []

    def get_cpu_usage(self):
        """Get CPU usage using 3-second moving average"""
        try:
            # Get new measurement with 1-second interval
            new_value = psutil.cpu_percent(interval=1.0)
            logger.debug(f"New CPU measurement: {new_value}%")
            
            # Update moving average
            self.cpu_values.append(new_value)
            if len(self.cpu_values) > self.window_size:
                self.cpu_values.pop(0)
            
            # Calculate average
            avg_value = mean(self.cpu_values)
            
            # Update last values
            self.last_cpu_value = avg_value
            self.last_cpu_measure_time = time.time()
            
            logger.debug(f"CPU measurements window: {self.cpu_values}, Average: {avg_value}%")
            return avg_value
            
        except Exception as e:
            logger.error(f"Error getting CPU usage: {str(e)}")
            return self.last_cpu_value if self.last_cpu_value is not None else 0

    def get_disk_usage(self):
        """Get disk usage with improved accuracy"""
        try:
            disk_info = {}
            # Get all physical drives
            for partition in psutil.disk_partitions(all=False):
                try:
                    # Skip non-fixed drives on Windows
                    if os.name == 'nt':
                        if 'fixed' not in partition.opts or not os.path.exists(partition.mountpoint):
                            continue
                    
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Only include if we can get valid readings and total space is significant
                    if usage.total > 1024 * 1024 * 1024:  # Only include drives larger than 1GB
                        disk_info[partition.mountpoint] = {
                            'device': partition.device,
                            'mountpoint': partition.mountpoint,
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'percent': usage.percent,
                            'opts': partition.opts
                        }
                        logger.debug(f"Disk {partition.mountpoint}: {usage.percent}% used")
                except PermissionError:
                    logger.debug(f"Permission denied for {partition.mountpoint}")
                    continue
                except Exception as e:
                    logger.error(f"Error reading disk {partition.mountpoint}: {str(e)}")
                    continue
            
            return disk_info
        except Exception as e:
            logger.error(f"Error in get_disk_usage: {str(e)}")
            return {}

# Create a global instance
system_stats = SystemStats()

def get_network_stats():
    net_io = psutil.net_io_counters()
    return {
        'bytes_sent': net_io.bytes_sent,
        'bytes_recv': net_io.bytes_recv,
        'packets_sent': net_io.packets_sent,
        'packets_recv': net_io.packets_recv
    }

def get_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            return {k: v[0].current for k, v in temps.items()}
    except:
        return {'cpu': 0}  # Fallback if temperature reading fails

def calculate_health_score(metrics):
    try:
        score = 100
        deductions = 0
        
        # CPU deduction
        if metrics['cpu_usage'] > HEALTH_THRESHOLDS['cpu']['critical']:
            deductions += 30
        elif metrics['cpu_usage'] > HEALTH_THRESHOLDS['cpu']['warning']:
            deductions += 15
        
        # Memory deduction
        if metrics['memory_usage'] > HEALTH_THRESHOLDS['memory']['critical']:
            deductions += 30
        elif metrics['memory_usage'] > HEALTH_THRESHOLDS['memory']['warning']:
            deductions += 15
        
        # Disk deduction - use the highest disk usage
        if metrics['disk_usage']:
            max_disk_usage = max(info['percent'] for info in metrics['disk_usage'].values())
            if max_disk_usage > HEALTH_THRESHOLDS['disk']['critical']:
                deductions += 20
            elif max_disk_usage > HEALTH_THRESHOLDS['disk']['warning']:
                deductions += 10
        
        # Temperature deduction
        temps = metrics.get('temperature', {})
        if isinstance(temps, dict) and 'cpu' in temps:
            cpu_temp = temps['cpu']
            if cpu_temp > HEALTH_THRESHOLDS['temperature']['critical']:
                deductions += 20
            elif cpu_temp > HEALTH_THRESHOLDS['temperature']['warning']:
                deductions += 10
        
        return max(0, score - deductions)
    except Exception as e:
        logger.error(f"Error in calculate_health_score: {str(e)}")
        return 50  # Return a default score on error

def check_alerts(metrics):
    try:
        alerts = []
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # CPU Alert
        if metrics['cpu_usage'] > HEALTH_THRESHOLDS['cpu']['critical']:
            alerts.append({
                'type': 'critical',
                'message': f'CPU usage critical: {metrics["cpu_usage"]:.1f}%',
                'timestamp': current_time
            })
        elif metrics['cpu_usage'] > HEALTH_THRESHOLDS['cpu']['warning']:
            alerts.append({
                'type': 'warning',
                'message': f'CPU usage high: {metrics["cpu_usage"]:.1f}%',
                'timestamp': current_time
            })
        
        # Memory Alert
        if metrics['memory_usage'] > HEALTH_THRESHOLDS['memory']['critical']:
            alerts.append({
                'type': 'critical',
                'message': f'Memory usage critical: {metrics["memory_usage"]:.1f}%',
                'timestamp': current_time
            })
        elif metrics['memory_usage'] > HEALTH_THRESHOLDS['memory']['warning']:
            alerts.append({
                'type': 'warning',
                'message': f'Memory usage high: {metrics["memory_usage"]:.1f}%',
                'timestamp': current_time
            })
        
        # Disk Alert - check each disk separately
        if metrics['disk_usage']:
            for mountpoint, info in metrics['disk_usage'].items():
                if info['percent'] > HEALTH_THRESHOLDS['disk']['critical']:
                    alerts.append({
                        'type': 'critical',
                        'message': f'Disk usage critical on {mountpoint}: {info["percent"]:.1f}%',
                        'timestamp': current_time
                    })
                elif info['percent'] > HEALTH_THRESHOLDS['disk']['warning']:
                    alerts.append({
                        'type': 'warning',
                        'message': f'Disk usage high on {mountpoint}: {info["percent"]:.1f}%',
                        'timestamp': current_time
                    })
        
        # Add new alerts to history
        for alert in alerts:
            alert_history.append(alert)
        
        # Keep only last 100 alerts
        while len(alert_history) > 100:
            alert_history.pop(0)
        
        return alerts
    except Exception as e:
        logger.error(f"Error in check_alerts: {str(e)}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def get_stats():
    try:
        logger.debug("Starting to collect system stats")
        
        # Get CPU usage with proper interval
        cpu_usage = system_stats.get_cpu_usage()
        logger.debug(f"CPU Usage: {cpu_usage}%")
        
        # Get memory information
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        logger.debug(f"Memory Usage: {memory_usage}%")
        
        # Get disk information
        disk_usage = system_stats.get_disk_usage()
        logger.debug(f"Disk Usage: {disk_usage}")
        
        # Use the highest disk usage value instead of average
        max_disk_usage = max((info['percent'] for info in disk_usage.values()), default=0)
        logger.debug(f"Max Disk Usage: {max_disk_usage}%")
        
        # Get processes (with proper CPU measurement)
        processes = []
        process_cpu = {}
        
        # First pass to initialize CPU measurements
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                proc.cpu_percent()
            except:
                continue
        
        # Wait a bit for accurate CPU measurements
        time.sleep(0.1)
        
        # Second pass to get actual values
        for proc in psutil.process_iter(['pid', 'name', 'memory_percent']):
            try:
                proc_info = proc.info
                # Skip System Idle Process
                if proc_info['name'].lower() in ['system idle process', 'idle']:
                    continue
                    
                cpu_percent = proc.cpu_percent()
                if cpu_percent > 0:
                    proc_info['cpu_percent'] = cpu_percent
                    processes.append(proc_info)
            except:
                continue
        
        # Sort by CPU usage and get top 10
        processes = sorted(processes, key=lambda x: x.get('cpu_percent', 0) or 0, reverse=True)[:10]
        
        # Prepare metrics for health scoring and alerts
        metrics = {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage,
            'temperature': get_temperature()
        }
        
        # Calculate health score and check alerts
        health_score = calculate_health_score(metrics)
        alerts = check_alerts(metrics)
        
        # Prepare response data
        response_data = {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'disk_usage': disk_usage,
            'system_disk_usage': max_disk_usage,  # Use max disk usage for the main display
            'processes': processes,
            'health_score': health_score,
            'alerts': alerts,
            'alert_history': alert_history[-10:]
        }
        
        return jsonify(response_data)
    except Exception as e:
        logger.error(f"Error in get_stats: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@app.route('/kill/<int:pid>', methods=['POST'])
def kill_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        return jsonify({'message': f'Process {pid} terminated successfully.'})
    except psutil.NoSuchProcess:
        return jsonify({'message': f'Process {pid} not found.'}), 404
    except psutil.AccessDenied:
        return jsonify({'message': f'Permission denied to terminate {pid}.'}), 403
    except Exception as e:
        logger.error(f"Error killing process {pid}: {str(e)}")
        return jsonify({'message': f'Error terminating {pid}: {str(e)}'}), 500

@app.route('/debug/cpu')
def debug_cpu():
    """Debug endpoint to check raw CPU values"""
    try:
        # Get raw CPU values
        raw_cpu = psutil.cpu_percent(interval=1.0)
        
        # Get our averaged value
        avg_cpu = system_stats.get_cpu_usage()
        
        return jsonify({
            'raw_cpu': raw_cpu,
            'averaged_cpu': avg_cpu,
            'measurement_window': system_stats.cpu_values,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        logger.error(f"Error in debug_cpu: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
