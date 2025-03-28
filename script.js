document.addEventListener("DOMContentLoaded", () => {
    initCharts();
    fetchStats();
    setInterval(fetchStats, 2000);
});

let cpuChart, memoryChart;

// Initialize Charts
function initCharts() {
    const ctxCpu = document.getElementById('cpuChart').getContext('2d');
    const ctxMemory = document.getElementById('memoryChart').getContext('2d');

    cpuChart = createChart(ctxCpu, "CPU Usage (%)", "blue");
    memoryChart = createChart(ctxMemory, "Memory Usage (%)", "red");
}

// Create a Chart.js Line Chart
function createChart(ctx, label, borderColor) {
    return new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label, data: [], borderColor, fill: false }] },
        options: { scales: { y: { beginAtZero: true, max: 100 } } }
    });
}

// Fetch System Stats
function fetchStats() {
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            updateStats(data);
            updateCharts(data.cpu_usage, data.memory_usage);
            updateProcessTable(data.processes);
        })
        .catch(error => console.error("Error fetching stats:", error));
}

// Update Dashboard Stats
function updateStats(data) {
    document.getElementById('cpu-usage').innerText = `${data.cpu_usage}%`;
    document.getElementById('memory-usage').innerText = `${data.memory_usage}%`;
    document.getElementById('total-processes').innerText = data.processes.length;

    // Smooth color transition for CPU & Memory Usage
    document.getElementById('cpu-usage').style.color = data.cpu_usage > 70 ? "red" : "lightgreen";
    document.getElementById('memory-usage').style.color = data.memory_usage > 70 ? "red" : "lightgreen";
}

// Update Charts
function updateCharts(cpuUsage, memoryUsage) {
    const time = new Date().toLocaleTimeString();

    updateChart(cpuChart, cpuUsage, time);
    updateChart(memoryChart, memoryUsage, time);
}

// Update Chart Data
function updateChart(chart, value, time) {
    chart.data.labels.push(time);
    chart.data.datasets[0].data.push(value);

    if (chart.data.labels.length > 10) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    chart.update();
}

// Update Process Table
function updateProcessTable(processes) {
    const processTable = document.getElementById('process-table');
    processTable.innerHTML = "";

    processes.forEach(proc => {
        const row = document.createElement("tr");
        row.style.color = proc.cpu_percent > 50 ? "red" : "white"; 

        row.innerHTML = `
            <td>${proc.pid}</td>
            <td>${proc.name}</td>
            <td>${proc.cpu_percent.toFixed(2)}%</td>
            <td>${proc.memory_percent.toFixed(2)}%</td>
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
            btn.closest("tr").remove();  // Remove the row instantly after killing the process
        })
        .catch(error => console.error("Error killing process:", error));
}
