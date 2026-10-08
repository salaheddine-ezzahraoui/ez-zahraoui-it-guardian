from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DashboardStats(BaseModel):
    total_assets: int
    online_assets: int
    offline_assets: int
    warning_assets: int
    maintenance_assets: int
    active_incidents: int
    critical_incidents: int
    high_incidents: int
    medium_incidents: int
    low_incidents: int
    overall_health: int
    production_health: int
    network_health: int
    server_health: int
    risk_score: int
    risk_band: str

    class Config:
        from_attributes = True

class AssetSummary(BaseModel):
    id: int
    hostname: str
    ip_address: str
    mac_address: Optional[str] = None
    asset_type: str
    operating_system: Optional[str] = None
    location: Optional[str] = None
    production_line: Optional[str] = None
    status: str
    owner_team: Optional[str] = None
    criticality: str
    description: Optional[str] = None
    is_active: bool
    last_check: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IncidentSummary(BaseModel):
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