import psutil
import time
import os
from datetime import datetime

def get_detailed_cpu():
    print("\nCPU Usage Measurements (1-second intervals):")
    # Initialize CPU measurement
    psutil.cpu_percent(interval=None)
    time.sleep(0.1)
    
    print("\nTaking measurements every second:")
    print("Time".ljust(12) + "| CPU Usage | Per Core Usage")
    print("-" * 70)
    
    for i in range(10):
        # Get measurements
        timestamp = datetime.now().strftime("%H:%M:%S")
        cpu = psutil.cpu_percent(interval=1)  # 1-second measurement
        per_cpu = psutil.cpu_percent(percpu=True)
        
        # Print with timestamp
        cores = ", ".join(f"{x:5.1f}%" for x in per_cpu)
        print(f"{timestamp} | {cpu:7.1f}% | {cores}")

def get_detailed_disk():
    print("\nDisk Usage Details:")
    all_partitions = psutil.disk_partitions(all=True)
    fixed_partitions = [p for p in all_partitions if 'fixed' in p.opts] if os.name == 'nt' else all_partitions
    
    print(f"\nFound {len(all_partitions)} total partitions, {len(fixed_partitions)} fixed drives")
    
    for partition in all_partitions:
        try:
            is_fixed = 'fixed' in partition.opts if os.name == 'nt' else True
            print(f"\nDrive {partition.mountpoint}")
            print(f"  Device: {partition.device}")
            print(f"  Type: {partition.fstype}")
            print(f"  Options: {partition.opts}")
            print(f"  Is Fixed: {is_fixed}")
            
            if os.path.exists(partition.mountpoint):
                usage = psutil.disk_usage(partition.mountpoint)
                print(f"  Usage: {usage.percent}%")
                print(f"  Total: {usage.total / (1024**3):.1f} GB")
                print(f"  Used:  {usage.used / (1024**3):.1f} GB")
                print(f"  Free:  {usage.free / (1024**3):.1f} GB")
            else:
                print("  Drive not accessible")
        except Exception as e:
            print(f"  Error reading drive: {str(e)}")

def get_memory_usage():
    memory = psutil.virtual_memory()
    print("\nMemory Usage Details:")
    print(f"  Total: {memory.total / (1024**3):.1f} GB")
    print(f"  Used:  {memory.used / (1024**3):.1f} GB")
    print(f"  Free:  {memory.free / (1024**3):.1f} GB")
    print(f"  Usage: {memory.percent}%")

print("=== System Diagnostic Tool ===")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print("\nMeasuring CPU usage...")
get_detailed_cpu()

print("\nChecking memory usage...")
get_memory_usage()

print("\nChecking disk usage...")
get_detailed_disk()

print(f"\nDiagnostic complete at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}") 