import webbrowser
import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SolarMatrix Asynchronous Real-Time Analytics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #38bdf8; margin-bottom: 5px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; text-align: center; }
        .card h3 { margin: 0; color: #94a3b8; font-size: 14px; text-transform: uppercase; }
        .card p { margin: 10px 0 0 0; font-size: 28px; font-weight: bold; color: #f1f5f9; }
        .chart-container { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 20px; height: 400px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; background: #1e293b; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { background-color: #0f172a; color: #38bdf8; }
        .badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .badge-danger { background: #ef4444; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h1>☀️ SolarMatrix Real-Time Analytics Hub</h1>
        <p style="color: #94a3b8; margin-top: 0;">Asynchronous Grid Ingestion & Task Queue Monitor</p>
        
        <div class="grid">
            <div class="card"><h3>Total Packets Ingested</h3><p id="total-packets">0</p></div>
            <div class="card"><h3>Total Active Output</h3><p id="total-power">0.00 W</p></div>
            <div class="card"><h3>Detected Fault Nodes</h3><p id="total-anomalies" style="color: #f87171;">0</p></div>
        </div>

        <div class="chart-container">
            <canvas id="powerChart"></canvas>
        </div>

        <h3>🚨 Critical Grid Anomalies Log</h3>
        <table>
            <thead>
                <tr><th>Timestamp</th><th>Node ID</th><th>Status Flag</th><th>Voltage</th><th>Irradiance</th></tr>
            </thead>
            <tbody id="anomaly-table">
                <tr><td colspan="5" style="text-align:center; color:#64748b;">Awaiting async queue telemetry processing...</td></tr>
            </tbody>
        </table>
    </div>

    <script>
        const ctx = document.getElementById('powerChart').getContext('2d');
        const powerChart = new Chart(ctx, {
            type: 'line',
            data: { labels: [], datasets: [] },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                animation: { duration: 400 }, // Smooth entry transitions for real-time streams
                scales: { 
                    y: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } }, 
                    x: { grid: { color: '#334155' }, ticks: { color: '#94a3b8' } } 
                } 
            }
        });

        const nodeColors = {
            'ARRAY-HSR-01': '#38bdf8', 'ARRAY-HSR-02': '#34d399',
            'ARRAY-WHITEFIELD-01': '#fbbf24', 'ARRAY-KORAMANGALA-01': '#c084fc'
        };

        async function updateDashboard() {
            try {
                const res = await fetch('http://127.0.0.1:8000/api/v1/telemetry/all');
                const data = await res.json();
                if(!data || data.length === 0) return;

                document.getElementById('total-packets').innerText = data.length;
                
                const totalPower = data.reduce((sum, item) => sum + item.power_output, 0);
                document.getElementById('total-power').innerText = totalPower.toFixed(2) + ' W';

                const anomalies = data.filter(item => item.status_flag !== 'NORMAL');
                document.getElementById('total-anomalies').innerText = anomalies.length;

                const tableBody = document.getElementById('anomaly-table');
                if(anomalies.length > 0) {
                    tableBody.innerHTML = anomalies.slice(0, 5).map(item => `
                        <tr>
                            <td>${new Date(item.timestamp).toLocaleTimeString()}</td>
                            <td><strong>${item.node_id}</strong></td>
                            <td><span class="badge badge-danger">${item.status_flag}</span></td>
                            <td>${item.voltage} V</td>
                            <td>${item.irradiance} W/m²</td>
                        </tr>
                    `).join('');
                } else {
                    tableBody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#64748b;">No active grid faults detected. System stable.</td></tr>`;
                }

                // Smoothly plot datasets across time coordinates
                const traceData = {};
                data.slice().reverse().forEach(item => {
                    if(!traceData[item.node_id]) traceData[item.node_id] = { labels: [], values: [] };
                    traceData[item.node_id].labels.push(new Date(item.timestamp).toLocaleTimeString());
                    traceData[item.node_id].values.push(item.power_output);
                });

                const datasets = Object.keys(traceData).map(nodeId => ({
                    label: nodeId,
                    data: traceData[nodeId].values,
                    borderColor: nodeColors[nodeId] || '#ffffff',
                    tension: 0.2,
                    fill: false,
                    pointRadius: 2
                }));

                const longestLabels = Object.values(traceData).reduce((max, curr) => curr.labels.length > max.length ? curr : max, {labels:[]}).labels;
                
                powerChart.data.labels = longestLabels;
                powerChart.data.datasets = datasets;
                powerChart.update();

            } catch (err) { console.error("FastAPI server thread cluster unreachable...", err); }
        }

        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
"""

file_path = os.path.abspath("live_dashboard.html")
with open(file_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"🌍 Launching Upgraded SolarMatrix Async Dashboard...")
webbrowser.open(f"file://{file_path}")