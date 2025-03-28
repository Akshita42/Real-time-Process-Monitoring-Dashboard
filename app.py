from flask import Flask, jsonify, render_template
import psutil
import os
import signal

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stats')
def get_stats():
    cpu_usage = psutil.cpu_percent(interval=0.1)
    memory_usage = psutil.virtual_memory().percent

    processes = []
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            proc_info = proc.info
            if not proc_info['name'] or proc_info['cpu_percent'] is None:
                continue  # Skip empty or invalid processes

            if proc_info['pid'] == 0:  
                continue  # Exclude System Idle Process

            # Fix CPU values > 100% (rare bug in psutil)
            proc_info['cpu_percent'] = min(proc_info['cpu_percent'], 100)

            processes.append(proc_info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Get top 10 high-CPU usage processes
    processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:10]

    return jsonify({
        'cpu_usage': cpu_usage,
        'memory_usage': memory_usage,
        'processes': processes
    })

@app.route('/kill/<int:pid>', methods=['POST'])
def kill_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.terminate()  # Safe termination
        return jsonify({'message': f'Process {pid} terminated successfully.'})
    except psutil.NoSuchProcess:
        return jsonify({'message': f'Process {pid} not found.'}), 404
    except psutil.AccessDenied:
        return jsonify({'message': f'Permission denied to terminate {pid}.'}), 403
    except Exception as e:
        return jsonify({'message': f'Error terminating {pid}: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
