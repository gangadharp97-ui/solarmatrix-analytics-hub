from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class SolarTelemetryInput(BaseModel):
    node_id: str = Field(..., example="ARRAY-HSR-01")
    voltage: float = Field(..., ge=0.0, le=50.0, description="Voltage in Volts")
    current: float = Field(..., ge=0.0, le=15.0, description="Current in Amperes")
    irradiance: float = Field(..., ge=0.0, le=1200.0, description="Solar intensity in W/m²")

class SolarTelemetryResponse(BaseModel):
    id: int
    node_id: str
    timestamp: datetime
    voltage: float
    current: float
    power_output: float  # Dynamically calculated: Voltage * Current
    irradiance: float
    status_flag: str

    class Config:
        from_attributes = True