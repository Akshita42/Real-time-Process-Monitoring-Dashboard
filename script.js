document.addEventListener("DOMContentLoaded", () => {
    console.log("Initializing application...");
    try {
        initCharts();
        console.log("Charts initialized successfully");
        fetchStats();
        setInterval(fetchStats, 2000);
    } catch (error) {
        console.error("Error during initialization:", error);
    }
});

let cpuChart, memoryChart, diskChart;

// Initialize Charts
function initCharts() {
    console.log("Starting chart initialization...");
    
    const ctxCpu = document.getElementById('cpuChart');
    const ctxMemory = document.getElementById('memoryChart');
    const ctxDisk = document.getElementById('diskChart');

    if (!ctxCpu || !ctxMemory || !ctxDisk) {
        throw new Error("Could not find one or more chart canvases");
    }

    console.log("Found all chart canvases");

    // Chart.js configuration
    const chartConfig = {
        type: 'line',
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)',
                    },
                    ticks: {
                        color: '#ffffff',
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#ffffff',
                        maxTicksLimit: 5
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            },
            animation: false
        }
    };

    try {
        // Create CPU Chart
        cpuChart = new Chart(ctxCpu, {
            ...chartConfig,
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            }
        });

        // Create Memory Chart
        memoryChart = new Chart(ctxMemory, {
            ...chartConfig,
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    borderColor: '#e74c3c',
                    backgroundColor: 'rgba(231, 76, 60, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            }
        });

        // Create Disk Chart
        diskChart = new Chart(ctxDisk, {
            ...chartConfig,
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            }
        });

        console.log("Charts created successfully");
    } catch (error) {
        console.error("Error creating charts:", error);
        throw error;
    }
}

// Fetch System Stats
function fetchStats() {
    console.log("Fetching stats...");
    fetch('/stats')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("Received data:", data);
            if (!data) {
                throw new Error('No data received from server');
            }
            updateStats(data);
            updateCharts(data);
            updateAlerts(data.alerts);
            updateAlertHistory(data.alert_history);
            updateHealthScore(data.health_score);
            updateProcessTable(data.processes);
        })
        .catch(error => {
            console.error("Error fetching stats:", error);
            document.getElementById('cpu-usage').innerText = 'Error';
            document.getElementById('memory-usage').innerText = 'Error';
            document.getElementById('disk-usage').innerText = 'Error';
        });
}

// Update Dashboard Stats
function updateStats(data) {
    try {
        // CPU Stats
        const cpuValue = parseFloat(data.cpu_usage).toFixed(1);
        document.getElementById('cpu-usage').innerText = `${cpuValue}%`;
        console.log("Updated CPU:", cpuValue);

        // Memory Stats
        const memoryValue = parseFloat(data.memory_usage).toFixed(1);
        document.getElementById('memory-usage').innerText = `${memoryValue}%`;
        console.log("Updated Memory:", memoryValue);

        // Disk Stats - use maximum disk usage
        const diskValue = parseFloat(data.system_disk_usage).toFixed(1);
        document.getElementById('disk-usage').innerText = `${diskValue}%`;
        console.log("Updated Disk:", diskValue);

        // Update detailed disk information
        const diskDetailsContainer = document.getElementById('disk-details');
        if (diskDetailsContainer) {
            diskDetailsContainer.innerHTML = '';
            Object.entries(data.disk_usage).forEach(([mountpoint, info]) => {
                const diskDetail = document.createElement('div');
                diskDetail.className = 'disk-detail';
                diskDetail.innerHTML = `
                    <span class="mount-point">${info.mountpoint}</span>
                    <span class="usage-value">${parseFloat(info.percent).toFixed(1)}%</span>
                `;
                diskDetailsContainer.appendChild(diskDetail);
            });
        }

        // Update charts with validated values
        if (cpuChart && typeof data.cpu_usage === 'number') {
            updateChart(cpuChart, Math.min(Math.max(data.cpu_usage, 0), 100), new Date().toLocaleTimeString());
        }
        if (memoryChart && typeof data.memory_usage === 'number') {
            updateChart(memoryChart, Math.min(Math.max(data.memory_usage, 0), 100), new Date().toLocaleTimeString());
        }
        if (diskChart && typeof data.system_disk_usage === 'number') {
            updateChart(diskChart, Math.min(Math.max(data.system_disk_usage, 0), 100), new Date().toLocaleTimeString());
        }
    } catch (error) {
        console.error("Error updating stats:", error);
    }
}

// Update Charts
function updateCharts(data) {
    try {
        const time = new Date().toLocaleTimeString();

        // Update CPU Chart with proper validation
        if (typeof data.cpu_usage === 'number' && !isNaN(data.cpu_usage)) {
            const cpuValue = Math.min(data.cpu_usage, 100);
            updateChart(cpuChart, cpuValue, time);
            console.log("Updated CPU chart:", cpuValue);
        }
        
        // Update Memory Chart with proper validation
        if (typeof data.memory_usage === 'number' && !isNaN(data.memory_usage)) {
            const memoryValue = Math.min(data.memory_usage, 100);
            updateChart(memoryChart, memoryValue, time);
            console.log("Updated Memory chart:", memoryValue);
        }
        
        // Update Disk Chart with proper validation
        if (data.disk_usage && Object.keys(data.disk_usage).length > 0) {
            const maxDiskUsage = Math.max(...Object.values(data.disk_usage).map(d => d.percent));
            if (!isNaN(maxDiskUsage)) {
                const diskValue = Math.min(maxDiskUsage, 100);
                updateChart(diskChart, diskValue, time);
                console.log("Updated Disk chart:", diskValue);
            }
        }
    } catch (error) {
        console.error("Error updating charts:", error);
    }
}

// Update Chart Data
function updateChart(chart, value, time) {
    try {
        if (!chart || !chart.data) {
            console.error("Invalid chart object");
            return;
        }

        // Ensure value is a valid number
        const numericValue = parseFloat(value);
        if (isNaN(numericValue)) {
            console.error('Invalid value for chart:', value);
            return;
        }

        // Keep only the last 30 data points
        if (chart.data.labels.length >= 30) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.data.labels.push(time);
        chart.data.datasets[0].data.push(numericValue);
        
        chart.update('none');  // Update without animation for better performance
    } catch (error) {
        console.error("Error updating chart:", error);
    }
}

// Update Alerts
function updateAlerts(alerts) {
    const alertsContainer = document.getElementById('alerts-container');
    alertsContainer.innerHTML = '';

    alerts.forEach(alert => {
        const alertElement = document.createElement('div');
        alertElement.className = `alert ${alert.type}`;
        alertElement.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${alert.message}</span>
        `;
        alertsContainer.appendChild(alertElement);
    });
}

// Update Alert History
function updateAlertHistory(history) {
    const historyContainer = document.getElementById('alert-history');
    historyContainer.innerHTML = '';

    history.forEach(alert => {
        const historyItem = document.createElement('div');
        historyItem.className = 'alert-history-item';
        historyItem.innerHTML = `
            <span class="message">${alert.message}</span>
            <span class="timestamp">${alert.timestamp}</span>
        `;
        historyContainer.appendChild(historyItem);
    });
}

// Update Health Score
function updateHealthScore(score) {
    const healthScoreElement = document.getElementById('health-score');
    healthScoreElement.innerText = score;
    
    // Update color based on score
    if (score >= 80) {
        healthScoreElement.style.backgroundColor = '#2ecc71'; // Green
    } else if (score >= 60) {
        healthScoreElement.style.backgroundColor = '#f39c12'; // Orange
    } else {
        healthScoreElement.style.backgroundColor = '#e74c3c'; // Red
    }
}

// Update Process Table
function updateProcessTable(processes) {
    const processTable = document.getElementById('process-table');
    processTable.innerHTML = '';

    processes.forEach(proc => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${proc.pid}</td>
            <td>${proc.name}</td>
            <td>${proc.cpu_percent.toFixed(1)}%</td>
            <td>${proc.memory_percent.toFixed(1)}%</td>
            <td><button class="kill-btn" onclick="killProcess(${proc.pid}, this)">Kill</button></td>
        `;
        processTable.appendChild(row);
    });
}

// Kill Process Function
function killProcess(pid, btn) {
    fetch(`/kill/${pid}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            btn.closest('tr').remove();
        })
        .catch(error => console.error('Error killing process:', error));
}
