import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# In-memory database keeps transactions incredibly fast for async threads
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL, 
    # 'check_same_thread': False allows background worker threads to share connections safely
    # StaticPool forces SQLAlchemy to keep a single, permanent connection open inside your RAM
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TelemetryRecord(Base):
    __tablename__ = "solar_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    voltage = Column(Float)
    current = Column(Float)
    power_output = Column(Float)
    irradiance = Column(Float)
    status_flag = Column(String, default="NORMAL")

def init_db():
    Base.metadata.create_all(bind=engine)