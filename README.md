# System Monitor

A real-time system monitoring web application built with Flask and psutil that provides detailed insights into your system's performance, including CPU, memory, disk usage, and process management.

## Features

- **Real-time System Metrics**
  - CPU usage monitoring with moving average
  - Memory usage tracking
  - Disk space monitoring
  - Network statistics
  - Temperature monitoring (where supported)

- **Process Management**
  - View running processes
  - Sort processes by CPU/memory usage
  - Terminate processes (with proper permissions)

- **Health Monitoring**
  - System health score calculation
  - Alert system for critical conditions
  - Historical alert tracking

- **User Interface**
  - Clean, modern dashboard
  - Real-time updates
  - Responsive design

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/system-monitor.git
cd system-monitor
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## API Endpoints

- `GET /` - Main dashboard
- `GET /stats` - Get system statistics
- `POST /kill/<pid>` - Terminate a process
- `GET /debug/cpu` - Debug CPU measurements

## Configuration

The application uses default thresholds for alerts:
- CPU: Warning (70%), Critical (90%)
- Memory: Warning (70%), Critical (90%)
- Disk: Warning (70%), Critical (90%)
- Temperature: Warning (70°C), Critical (85°C)

## Security Considerations

- Process termination requires proper system permissions
- The application should be run with appropriate user privileges
- Consider using HTTPS in production environments





## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - Web framework
- [psutil](https://psutil.readthedocs.io/) - System monitoring library 
