import psutil
import time
from statistics import mean
import logging
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_system_cpu_info():
    """Get detailed CPU information"""
    print("\n=== System CPU Information ===")
    print(f"Physical cores: {psutil.cpu_count(logical=False)}")
    print(f"Total cores: {psutil.cpu_count(logical=True)}")
    print(f"CPU frequency: {psutil.cpu_freq().current} MHz")
    print(f"CPU usage per core: {psutil.cpu_percent(interval=1.0, percpu=True)}")

def verify_cpu_measurements():
    """Verify CPU usage measurements"""
    print("\n=== CPU Usage Verification Test ===")
    
    # Get system CPU info first
    get_system_cpu_info()
    
    # Test 1: Verify raw CPU measurement with different intervals
    print("\nTest 1: Raw CPU Measurement with Different Intervals")
    intervals = [0.1, 0.5, 1.0, 2.0]
    for interval in intervals:
        raw_cpu = psutil.cpu_percent(interval=interval)
        print(f"Interval {interval}s: {raw_cpu}%")
    
    # Test 2: Verify multiple measurements with per-core data
    print("\nTest 2: Multiple Measurements with Per-Core Data")
    for i in range(3):
        print(f"\nMeasurement {i+1}:")
        per_cpu = psutil.cpu_percent(interval=1.0, percpu=True)
        total_cpu = psutil.cpu_percent(interval=1.0)
        print(f"Per-core usage: {per_cpu}")
        print(f"Total CPU usage: {total_cpu}%")
    
    # Test 3: Verify moving window with detailed logging
    print("\nTest 3: Moving Window Test with Detailed Logging")
    window_size = 3
    window = []
    for i in range(10):
        # Get both total and per-core measurements
        total_cpu = psutil.cpu_percent(interval=1.0)
        per_cpu = psutil.cpu_percent(interval=1.0, percpu=True)
        
        window.append(total_cpu)
        if len(window) > window_size:
            window.pop(0)
        avg = mean(window)
        
        print(f"\nMeasurement {i+1}:")
        print(f"Total CPU: {total_cpu}%")
        print(f"Per-core usage: {per_cpu}")
        print(f"Window values: {window}")
        print(f"Moving average: {avg}%")
        
        # Add a small delay to see changes
        time.sleep(0.5)
    
    # Test 4: Compare with system load
    print("\nTest 4: System Load Comparison")
    print("Please run some CPU-intensive tasks and observe the values")
    print("The values should increase with CPU load")
    
    # Test 5: Verify with different measurement methods
    print("\nTest 5: Different Measurement Methods")
    print("Method 1: psutil.cpu_percent()")
    print(f"Result: {psutil.cpu_percent(interval=1.0)}%")
    
    print("\nMethod 2: psutil.cpu_times_percent()")
    print(f"Result: {psutil.cpu_times_percent(interval=1.0)}")

if __name__ == "__main__":
    verify_cpu_measurements() 