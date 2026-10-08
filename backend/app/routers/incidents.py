from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.incident import Incident, IncidentStatus, IncidentSeverity, IncidentPriority, IncidentCategory
from app.models.asset import Asset
from app.services.incident_manager import IncidentManager
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    assigned_technician: Optional[str] = None
    resolution_notes: Optional[str] = None
    root_cause: Optional[str] = None

class IncidentResponse(BaseModel):
    id: int
    incident_id: str
    asset_id: int
    category: str
    severity: str
    priority: str
    status: str
    title: str
    description: Optional[str] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    assigned_technician: Optional[str] = None
    root_cause: Optional[str] = None
    resolution_notes: Optional[str] = None
    risk_score: Optional[float] = None
    production_impact: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/api/incidents", response_model=List[IncidentResponse])
def list_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if status:
        query = query.filter(Incident.status == status)
    if severity:
        query = query.filter(Incident.severity == severity)
    return query.order_by(Incident.detected_at.desc()).offset(skip).limit(limit).all()

@router.get("/api/incidents/{incident_id}", response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident

@router.patch("/api/incidents/{incident_id}", response_model=IncidentResponse)
def update_incident(incident_id: int, update: IncidentUpdate, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if update.status:
        incident.status = update.status
        if update.status == "resolved":
            incident.resolved_at = datetime.utcnow()
    if update.assigned_technician:
        incident.assigned_technician = update.assigned_technician
    if update.resolution_notes:
        incident.resolution_notes = update.resolution_notes
    if update.root_cause:
        incident.root_cause = update.root_cause

    db.commit()
    db.refresh(incident)
    return incident

@router.post("/api/incidents/{incident_id}/assign")
def assign_incident(incident_id: int, technician: str, db: Session = Depends(get_db)):
    manager = IncidentManager(db)
    incident = manager.assign_technician(incident_id, technician)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"message": f"Incident assigned to {technician}"}

@router.post("/api/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: int, notes: str, root_cause: Optional[str] = None, db: Session = Depends(get_db)):
    manager = IncidentManager(db)
    incident = manager.resolve_incident(incident_id, notes, root_cause)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"message": "Incident resolved"}

@router.get("/api/incidents/active")
def get_active_incidents(db: Session = Depends(get_db)):
    manager = IncidentManager(db)
    return manager.get_active_incidents()

@router.post("/api/incidents/escalate")
def escalate_incidents(db: Session = Depends(get_db)):
    manager = IncidentManager(db)
    count = manager.escalate_unresolved_incidents()
    return {"message": f"{count} incidents escalated"}
