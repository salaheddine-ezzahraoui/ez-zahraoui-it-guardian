from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from app.database import get_db
from app.models.asset import Asset, AssetStatus, AssetType, CriticalityLevel
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.event import Event, EventType
from app.schemas.dashboard import DashboardStats, AssetSummary, IncidentSummary
from typing import List
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/api/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Asset counts by status
    total_assets = db.query(Asset).filter(Asset.is_active == True).count()
    online_assets = db.query(Asset).filter(Asset.status == AssetStatus.ONLINE).count()
    offline_assets = db.query(Asset).filter(Asset.status == AssetStatus.OFFLINE).count()
    warning_assets = db.query(Asset).filter(Asset.status == AssetStatus.WARNING).count()
    maintenance_assets = db.query(Asset).filter(Asset.status == AssetStatus.MAINTENANCE).count()

    # Incident counts
    active_incidents = db.query(Incident).filter(
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
    ).count()
    critical_incidents = db.query(Incident).filter(
        Incident.severity == IncidentSeverity.CRITICAL,
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
    ).count()
    high_incidents = db.query(Incident).filter(
        Incident.severity == IncidentSeverity.HIGH,
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
    ).count()
    medium_incidents = db.query(Incident).filter(
        Incident.severity == IncidentSeverity.MEDIUM,
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
    ).count()
    low_incidents = db.query(Incident).filter(
        Incident.severity == IncidentSeverity.LOW,
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
    ).count()

    # Calculate health scores
    if total_assets > 0:
        overall_health = int((online_assets / total_assets) * 100)
    else:
        overall_health = 100

    # Production health (assets on production lines)
    prod_assets = db.query(Asset).filter(Asset.production_line.isnot(None)).count()
    prod_online = db.query(Asset).filter(
        Asset.production_line.isnot(None),
        Asset.status == AssetStatus.ONLINE
    ).count()
    production_health = int((prod_online / prod_assets) * 100) if prod_assets > 0 else 100

    # Network health (switches and routers)
    network_assets = db.query(Asset).filter(
        Asset.asset_type.in_([AssetType.SWITCH, AssetType.ROUTER])
    ).count()
    network_online = db.query(Asset).filter(
        Asset.asset_type.in_([AssetType.SWITCH, AssetType.ROUTER]),
        Asset.status == AssetStatus.ONLINE
    ).count()
    network_health = int((network_online / network_assets) * 100) if network_assets > 0 else 100

    # Server health
    server_assets = db.query(Asset).filter(Asset.asset_type == AssetType.SERVER).count()
    server_online = db.query(Asset).filter(
        Asset.asset_type == AssetType.SERVER,
        Asset.status == AssetStatus.ONLINE
    ).count()
    server_health = int((server_online / server_assets) * 100) if server_assets > 0 else 100

    # Risk score calculation
    risk_score = 0
    if total_assets > 0:
        risk_score += int((offline_assets / total_assets) * 30)
        risk_score += int((warning_assets / total_assets) * 15)
    risk_score += min(critical_incidents * 15, 30)
    risk_score += min(high_incidents * 8, 16)
    risk_score += min(medium_incidents * 3, 9)
    risk_score = min(risk_score, 100)

    # Risk band
    if risk_score <= 30:
        risk_band = "LOW"
    elif risk_score <= 60:
        risk_band = "MEDIUM"
    elif risk_score <= 80:
        risk_band = "HIGH"
    else:
        risk_band = "CRITICAL"

    return DashboardStats(
        total_assets=total_assets,
        online_assets=online_assets,
        offline_assets=offline_assets,
        warning_assets=warning_assets,
        maintenance_assets=maintenance_assets,
        active_incidents=active_incidents,
        critical_incidents=critical_incidents,
        high_incidents=high_incidents,
        medium_incidents=medium_incidents,
        low_incidents=low_incidents,
        overall_health=overall_health,
        production_health=production_health,
        network_health=network_health,
        server_health=server_health,
        risk_score=risk_score,
        risk_band=risk_band,
    )

@router.get("/api/assets", response_model=List[AssetSummary])
def get_assets(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    assets = db.query(Asset).filter(Asset.is_active == True).offset(skip).limit(limit).all()
    return assets

@router.get("/api/incidents", response_model=List[IncidentSummary])
def get_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    incidents = db.query(Incident).order_by(Incident.detected_at.desc()).offset(skip).limit(limit).all()
    return incidents

@router.get("/api/events")
def get_events(limit: int = 20, db: Session = Depends(get_db)):
    events = db.query(Event).order_by(Event.created_at.desc()).limit(limit).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type.value if hasattr(e.event_type, 'value') else str(e.event_type),
            "message": e.message,
            "created_at": e.created_at.isoformat() if e.created_at else None,
        }
        for e in events
    ]

@router.get("/api/assets/by-status")
def get_assets_by_status(db: Session = Depends(get_db)):
    """Get asset counts grouped by status for charts"""
    results = db.query(
        Asset.status,
        func.count(Asset.id).label('count')
    ).filter(Asset.is_active == True).group_by(Asset.status).all()
    
    return [
        {
            "status": r.status.value if hasattr(r.status, 'value') else str(r.status),
            "count": r.count
        }
        for r in results
    ]

@router.get("/api/assets/by-type")
def get_assets_by_type(db: Session = Depends(get_db)):
    """Get asset counts grouped by type for charts"""
    results = db.query(
        Asset.asset_type,
        func.count(Asset.id).label('count')
    ).filter(Asset.is_active == True).group_by(Asset.asset_type).all()
    
    return [
        {
            "type": r.asset_type.value if hasattr(r.asset_type, 'value') else str(r.asset_type),
            "count": r.count
        }
        for r in results
    ]

@router.get("/api/incidents/by-severity")
def get_incidents_by_severity(db: Session = Depends(get_db)):
    """Get incident counts grouped by severity"""
    results = db.query(
        Incident.severity,
        func.count(Incident.id).label('count')
    ).filter(
        Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
    ).group_by(Incident.severity).all()
    
    return [
        {
            "severity": r.severity.value if hasattr(r.severity, 'value') else str(r.severity),
            "count": r.count
        }
        for r in results
    ]

@router.get("/api/incidents/by-status")
def get_incidents_by_status(db: Session = Depends(get_db)):
    """Get incident counts grouped by status"""
    results = db.query(
        Incident.status,
        func.count(Incident.id).label('count')
    ).group_by(Incident.status).all()
    
    return [
        {
            "status": r.status.value if hasattr(r.status, 'value') else str(r.status),
            "count": r.count
        }
        for r in results
    ]

@router.get("/api/production-lines")
def get_production_lines(db: Session = Depends(get_db)):
    """Get production line health data"""
    results = db.query(
        Asset.production_line,
        func.count(Asset.id).label('total'),
        func.sum(case((Asset.status == AssetStatus.ONLINE, 1), else_=0)).label('online'),
        func.sum(case((Asset.status == AssetStatus.OFFLINE, 1), else_=0)).label('offline'),
        func.sum(case((Asset.status == AssetStatus.WARNING, 1), else_=0)).label('warning'),
    ).filter(
        Asset.production_line.isnot(None),
        Asset.is_active == True
    ).group_by(Asset.production_line).all()
    
    return [
        {
            "line": r.production_line,
            "total": r.total,
            "online": r.online or 0,
            "offline": r.offline or 0,
            "warning": r.warning or 0,
            "health": int(((r.online or 0) / r.total) * 100) if r.total > 0 else 100
        }
        for r in results
    ]
