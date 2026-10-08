from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.incident import Incident
from app.services.ai_troubleshoot import AITroubleshooter
import os

router = APIRouter()

@router.get("/api/ai/analyze/{incident_id}")
def analyze_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")

    troubleshooter = AITroubleshooter(db, ollama_url, model)
    return troubleshooter.analyze_incident(incident_id)

@router.get("/api/ai/health")
def ai_health():
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "llama3.2")
    
    return {
        "ollama_url": ollama_url,
        "model": model,
        "status": "configured"
    }