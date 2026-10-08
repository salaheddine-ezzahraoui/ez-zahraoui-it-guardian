from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class IncidentCategory(str, enum.Enum):
    NETWORK = "network"
    SERVER = "server"
    WORKSTATION = "workstation"
    APPLICATION = "application"
    HARDWARE = "hardware"
    SECURITY = "security"
    CLOUD = "cloud"
    OTHER = "other"

class IncidentSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, enum.Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class IncidentPriority(str, enum.Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    incident_id = Column(String(20), unique=True, nullable=False, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    category = Column(Enum(IncidentCategory), nullable=False)
    severity = Column(Enum(IncidentSeverity), nullable=False)
    priority = Column(Enum(IncidentPriority), nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    assigned_technician = Column(String(100), nullable=True)
    root_cause = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    risk_score = Column(Float, nullable=True)
    production_impact = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    asset = relationship("Asset", backref="incidents")

    def __repr__(self):
        return f"<Incident(id='{self.incident_id}', severity='{self.severity}', status='{self.status}')>"
