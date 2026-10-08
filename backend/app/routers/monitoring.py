from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.monitoring import MonitoringResult, CheckType, CheckResult
from app.models.asset import Asset
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class MonitoringResultResponse(BaseModel):
    id: int
    asset_id: int
    check_type: str
    result: str
    response_time_ms: Optional[float] = None
    packet_loss_percent: Optional[float] = None
    status_code: Optional[int] = None
    message: Optional[str] = None
    checked_at: datetime
    asset_hostname: Optional[str] = None

    class Config:
        from_attributes = True

@router.get("/api/monitoring/results", response_model=List[MonitoringResultResponse])
def get_monitoring_results(
    check_type: Optional[str] = None,
    result: Optional[str] = None,
    asset_id: Optional[int] = None,
    limit: int = 50,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(MonitoringResult, Asset.hostname.label('asset_hostname')).join(
        Asset, MonitoringResult.asset_id == Asset.id
    )

    if check_type:
        query = query.filter(MonitoringResult.check_type == check_type)
    if result:
        query = query.filter(MonitoringResult.result == result)
    if asset_id:
        query = query.filter(MonitoringResult.asset_id == asset_id)

    results = query.order_by(MonitoringResult.checked_at.desc()).offset(skip).limit(limit).all()

    return [
        MonitoringResultResponse(
            id=r.MonitoringResult.id,
            asset_id=r.MonitoringResult.asset_id,
            check_type=r.MonitoringResult.check_type.value if hasattr(r.MonitoringResult.check_type, 'value') else str(r.MonitoringResult.check_type),
            result=r.MonitoringResult.result.value if hasattr(r.MonitoringResult.result, 'value') else str(r.MonitoringResult.result),
            response_time_ms=r.MonitoringResult.response_time_ms,
            packet_loss_percent=r.MonitoringResult.packet_loss_percent,
            status_code=r.MonitoringResult.status_code,
            message=r.MonitoringResult.message,
            checked_at=r.MonitoringResult.checked_at,
            asset_hostname=r.asset_hostname,
        )
        for r in results
    ]

@router.get("/api/monitoring/results/{result_id}", response_model=MonitoringResultResponse)
def get_monitoring_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(MonitoringResult, Asset.hostname.label('asset_hostname')).join(
        Asset, MonitoringResult.asset_id == Asset.id
    ).filter(MonitoringResult.id == result_id).first()

    if not result:
        return None

    r = result
    return MonitoringResultResponse(
        id=r.MonitoringResult.id,
        asset_id=r.MonitoringResult.asset_id,
        check_type=r.MonitoringResult.check_type.value if hasattr(r.MonitoringResult.check_type, 'value') else str(r.MonitoringResult.check_type),
        result=r.MonitoringResult.result.value if hasattr(r.MonitoringResult.result, 'value') else str(r.MonitoringResult.result),
        response_time_ms=r.MonitoringResult.response_time_ms,
        packet_loss_percent=r.MonitoringResult.packet_loss_percent,
        status_code=r.MonitoringResult.status_code,
        message=r.MonitoringResult.message,
        checked_at=r.MonitoringResult.checked_at,
        asset_hostname=r.asset_hostname,
    )

@router.get("/api/monitoring/summary")
def get_monitoring_summary(db: Session = Depends(get_db)):
    from sqlalchemy import func

    # Count by check type and result
    stats = db.query(
        MonitoringResult.check_type,
        MonitoringResult.result,
        func.count(MonitoringResult.id).label('count')
    ).group_by(MonitoringResult.check_type, MonitoringResult.result).all()

    summary = {}
    for s in stats:
        ct = s.check_type.value if hasattr(s.check_type, 'value') else str(s.check_type)
        res = s.result.value if hasattr(s.result, 'value') else str(s.result)
        if ct not in summary:
            summary[ct] = {}
        summary[ct][res] = s.count

    # Average response time
    avg_response = db.query(func.avg(MonitoringResult.response_time_ms)).filter(
        MonitoringResult.response_time_ms.isnot(None)
    ).scalar()

    # Total checks in last 24 hours
    from datetime import timedelta
    recent_count = db.query(func.count(MonitoringResult.id)).filter(
        MonitoringResult.checked_at > datetime.utcnow() - timedelta(hours=24)
    ).scalar()

    return {
        "breakdown": summary,
        "average_response_time_ms": round(avg_response, 2) if avg_response else None,
        "checks_last_24h": recent_count,
    }
