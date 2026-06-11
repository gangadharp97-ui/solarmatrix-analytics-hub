# ☀️ SolarMatrix Analytics Hub
### Asynchronous IoT Ingestion Pipeline & Real-Time Grid Anomaly Monitor

A high-throughput, three-tier distributed architecture built to ingest, calculate, and evaluate real-time hardware telemetry streams from widespread solar arrays. 

This project demonstrates a production-ready solution to database write-locks and network I/O bottlenecks by utilizing an asynchronous non-blocking worker thread-pool design.

🔗 **[Live Interactive Dashboard Demo](https://gangadharp97-ui.github.io/solarmatrix-analytics-hub/)**

---

## 🏗️ System Architecture & Data Flow

The application splits computational workloads across three decoupled operational layers to ensure microsecond-scale request handling:

1. **The Edge Simulator (`simulator.py`):** Simulates physical solar array nodes generating high-frequency electrical fields (Voltage, Current, and Irradiance) and periodically injecting fault states.
2. **The Ingestion Gateway Core (`main.py` & `database.py`):** An asynchronous FastAPI engine that accepts payloads, instantly releases the connection back to the edge with an HTTP `202 Accepted` status, and delegates processing to background worker queues.
3. **The Presentation UI (`index.html`):** A client-side visualizer using Chart.js to parse real-time database JSON feeds into smooth, live-ticking moving line charts and critical fault logs.