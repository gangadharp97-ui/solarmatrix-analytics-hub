from fastapi import FastAPI, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models
import database

# Initialize the FastAPI App Engine with Production Configuration
app = FastAPI(
    title="SolarMatrix Analytics Hub", 
    version="2.0.0",
    description="Production-Grade Asynchronous IoT Solar Telemetry Pipeline"
)

# --- CORS MIDDLEWARE CONFIGURATION ---
# Allows your frontend dashboards, external services, and Swagger UI 
# to fetch data cleanly without cross-origin security blocks.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize in-memory database schema on server startup
@app.on_event("startup")
def startup_event():
    database.init_db()

# Dependency injection provider to provision database sessions per request thread
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- ASYNCHRONOUS BACKGROUND WORKER ---
def process_telemetry_worker(payload_dict: dict, db_session: Session):
    """
    Background Worker: Safely handles intensive data calculations, 
    algorithmic anomaly tracking, and database commits entirely outside 
    the core API request-response lifecycle.
    """
    voltage = payload_dict["voltage"]
    current = payload_dict["current"]
    irradiance = payload_dict["irradiance"]
    
    # Calculate electrical power throughput
    calculated_power = round(voltage * current, 2)
    
    # Execute Algorithmic Rule Engine for Fault Detection
    flag = "NORMAL"
    if irradiance > 700.0 and voltage < 12.0:
        flag = "ANOMALY_LOW_EFFICIENCY"
    elif voltage == 0.0 or current == 0.0:
        flag = "NODE_OFFLINE"

    # Commit record straight into the database configuration layer
    db_record = database.TelemetryRecord(
        node_id=payload_dict["node_id"],
        voltage=voltage,
        current=current,
        power_output=calculated_power,
        irradiance=irradiance,
        status_flag=flag
    )
    db_session.add(db_record)
    db_session.commit()


# --- API CORE ENDPOINTS ---

@app.post("/api/v1/telemetry", status_code=status.HTTP_202_ACCEPTED)
def ingest_telemetry_async(
    payload: models.SolarTelemetryInput, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    """
    Ingestion Core: Accepts incoming data packets, returns an HTTP 202 
    Accepted status instantly to the edge device, and offloads heavy database 
    processing to background worker threads. Completely mitigates network I/O blockages.
    """
    # Serialize the Pydantic data model into a plain dictionary payload
    payload_dict = payload.dict()
    
    # Hand off the calculation and insertion workload to the async task worker pool
    background_tasks.add_task(process_telemetry_worker, payload_dict, db)
    
    # Instantly release the connection back to the edge simulator
    return {
        "status": "accepted", 
        "message": "Telemetry packet successfully queued for ingestion pipeline"
    }


@app.get("/api/v1/telemetry/anomalies", response_model=List[models.SolarTelemetryResponse])
def get_grid_anomalies(db: Session = Depends(get_db)):
    """
    Monitoring Endpoint: Queries and returns an historical list 
    of failed grid connections or malfunctioning hardware setups.
    """
    return db.query(database.TelemetryRecord)\
             .filter(database.TelemetryRecord.status_flag != "NORMAL")\
             .all()


@app.get("/api/v1/telemetry/all", response_model=List[models.SolarTelemetryResponse])
def get_all_telemetry(db: Session = Depends(get_db)):
    """
    Dashboard Feed: Fetches the latest 100 historical telemetry sweeps 
    ordered dynamically to feed live browser chart panels.
    """
    return db.query(database.TelemetryRecord)\
             .order_by(database.TelemetryRecord.id.desc())\
             .limit(100)\
             .all()