from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.asset import Asset, AssetStatus, CriticalityLevel
from app.models.incident import Incident, IncidentCategory, IncidentSeverity, IncidentStatus, IncidentPriority
from app.models.event import Event, EventType

class IncidentManager:
    """Manages automatic incident creation and escalation"""

    def __init__(self, db: Session):
        self.db = db

    def check_and_create_incident(self, asset: Asset, old_status: AssetStatus, new_status: AssetStatus):
        """Check if an incident should be created based on status change"""
        if old_status == new_status:
            return None

        # Asset went offline
        if new_status == AssetStatus.OFFLINE:
            return self._create_offline_incident(asset)

        # Asset went to warning
        if new_status == AssetStatus.WARNING:
            return self._create_warning_incident(asset)

        # Asset recovered
        if new_status == AssetStatus.ONLINE and old_status in [AssetStatus.OFFLINE, AssetStatus.WARNING]:
            return self._resolve_incidents_for_asset(asset)

        return None

    def _create_offline_incident(self, asset: Asset):
        """Create an incident for an offline asset"""
        # Check for existing active incident
        existing = self.db.query(Incident).filter(
            Incident.asset_id == asset.id,
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
        ).first()

        if existing:
            return None

        # Determine severity and priority based on criticality
        if asset.criticality == CriticalityLevel.CRITICAL:
            severity = IncidentSeverity.CRITICAL
            priority = IncidentPriority.P1
        elif asset.criticality == CriticalityLevel.HIGH:
            severity = IncidentSeverity.HIGH
            priority = IncidentPriority.P2
        elif asset.criticality == CriticalityLevel.MEDIUM:
            severity = IncidentSeverity.MEDIUM
            priority = IncidentPriority.P3
        else:
            severity = IncidentSeverity.LOW
            priority = IncidentPriority.P4

        # Determine category based on asset type
        category = self._get_category_for_asset(asset)

        # Generate incident ID
        incident_id = self._generate_incident_id()

        # Create incident
        incident = Incident(
            incident_id=incident_id,
            asset_id=asset.id,
            category=category,
            severity=severity,
            priority=priority,
            status=IncidentStatus.OPEN,
            title=f"{asset.hostname} is offline",
            description=f"{asset.hostname} ({asset.ip_address}) is not responding to monitoring checks. "
                       f"Location: {asset.location or 'Unknown'}. "
                       f"Production Line: {asset.production_line or 'N/A'}. "
                       f"Criticality: {asset.criticality.value}.",
            detected_at=datetime.utcnow(),
            production_impact=self._calculate_production_impact(asset),
        )

        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        # Create event
        event = Event(
            event_type=EventType.INCIDENT_CREATED,
            message=f"Incident {incident_id} created: {asset.hostname} is offline",
            asset_id=asset.id,
            incident_id=incident.id,
        )
        self.db.add(event)
        self.db.commit()

        return incident

    def _create_warning_incident(self, asset: Asset):
        """Create an incident for a warning asset"""
        # Only create incidents for high/critical assets in warning state
        if asset.criticality not in [CriticalityLevel.HIGH, CriticalityLevel.CRITICAL]:
            return None

        # Check for existing active incident
        existing = self.db.query(Incident).filter(
            Incident.asset_id == asset.id,
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
        ).first()

        if existing:
            return None

        incident_id = self._generate_incident_id()

        incident = Incident(
            incident_id=incident_id,
            asset_id=asset.id,
            category=self._get_category_for_asset(asset),
            severity=IncidentSeverity.MEDIUM,
            priority=IncidentPriority.P3,
            status=IncidentStatus.OPEN,
            title=f"{asset.hostname} performance degraded",
            description=f"{asset.hostname} ({asset.ip_address}) is showing warning signs. "
                       f"Location: {asset.location or 'Unknown'}. "
                       f"Production Line: {asset.production_line or 'N/A'}.",
            detected_at=datetime.utcnow(),
        )

        self.db.add(incident)
        self.db.commit()
        self.db.refresh(incident)

        event = Event(
            event_type=EventType.INCIDENT_CREATED,
            message=f"Incident {incident_id} created: {asset.hostname} performance degraded",
            asset_id=asset.id,
            incident_id=incident.id,
        )
        self.db.add(event)
        self.db.commit()

        return incident

    def _resolve_incidents_for_asset(self, asset: Asset):
        """Resolve all active incidents for an asset that recovered"""
        active_incidents = self.db.query(Incident).filter(
            Incident.asset_id == asset.id,
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
        ).all()

        for incident in active_incidents:
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = datetime.utcnow()
            incident.resolution_notes = "Asset recovered automatically by monitoring system"

            event = Event(
                event_type=EventType.INCIDENT_RESOLVED,
                message=f"Incident {incident.incident_id} auto-resolved: {asset.hostname} recovered",
                asset_id=asset.id,
                incident_id=incident.id,
            )
            self.db.add(event)

        self.db.commit()
        return active_incidents

    def _generate_incident_id(self) -> str:
        """Generate a unique incident ID"""
        count = self.db.query(Incident).count()
        return f"INC-{1043 + count}"

    def _get_category_for_asset(self, asset: Asset) -> IncidentCategory:
        """Determine incident category based on asset type"""
        from app.models.asset import AssetType

        if asset.asset_type == AssetType.SERVER:
            return IncidentCategory.SERVER
        elif asset.asset_type == AssetType.PRODUCTION_PC:
            return IncidentCategory.WORKSTATION
        elif asset.asset_type in [AssetType.SWITCH, AssetType.ROUTER]:
            return IncidentCategory.NETWORK
        elif asset.asset_type == AssetType.APPLICATION:
            return IncidentCategory.APPLICATION
        elif asset.asset_type == AssetType.PRINTER:
            return IncidentCategory.HARDWARE
        else:
            return IncidentCategory.OTHER

    def _calculate_production_impact(self, asset: Asset) -> str:
        """Calculate production impact based on asset criticality and production line"""
        if asset.criticality == CriticalityLevel.CRITICAL:
            return "CRITICAL"
        elif asset.criticality == CriticalityLevel.HIGH and asset.production_line:
            return "HIGH"
        elif asset.production_line:
            return "MEDIUM"
        else:
            return "LOW"

    def escalate_unresolved_incidents(self):
        """Escalate incidents that have been open for too long"""
        now = datetime.utcnow()

        # Escalate P1 incidents open for > 30 minutes
        p1_old = self.db.query(Incident).filter(
            Incident.priority == IncidentPriority.P1,
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]),
            Incident.detected_at < now - timedelta(minutes=30)
        ).all()

        for incident in p1_old:
            event = Event(
                event_type=EventType.INCIDENT_UPDATED,
                message=f"Incident {incident.incident_id} escalated: P1 open for > 30 minutes",
                incident_id=incident.id,
            )
            self.db.add(event)

        # Escalate P2 incidents open for > 2 hours
        p2_old = self.db.query(Incident).filter(
            Incident.priority == IncidentPriority.P2,
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING]),
            Incident.detected_at < now - timedelta(hours=2)
        ).all()

        for incident in p2_old:
            event = Event(
                event_type=EventType.INCIDENT_UPDATED,
                message=f"Incident {incident.incident_id} escalated: P2 open for > 2 hours",
                incident_id=incident.id,
            )
            self.db.add(event)

        self.db.commit()
        return len(p1_old) + len(p2_old)

    def get_active_incidents(self):
        """Get all active incidents"""
        return self.db.query(Incident).filter(
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
        ).order_by(Incident.detected_at.desc()).all()

    def assign_technician(self, incident_id: int, technician: str):
        """Assign a technician to an incident"""
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if incident:
            incident.assigned_technician = technician
            incident.status = IncidentStatus.IN_PROGRESS
            self.db.commit()

            event = Event(
                event_type=EventType.INCIDENT_UPDATED,
                message=f"Incident {incident.incident_id} assigned to {technician}",
                incident_id=incident.id,
            )
            self.db.add(event)
            self.db.commit()
            return incident
        return None

    def resolve_incident(self, incident_id: int, resolution_notes: str, root_cause: str = None):
        """Resolve an incident"""
        incident = self.db.query(Incident).filter(Incident.id == incident_id).first()
        if incident:
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = datetime.utcnow()
            incident.resolution_notes = resolution_notes
            incident.root_cause = root_cause
            self.db.commit()

            event = Event(
                event_type=EventType.INCIDENT_RESOLVED,
                message=f"Incident {incident.incident_id} resolved",
                incident_id=incident.id,
            )
            self.db.add(event)
            self.db.commit()
            return incident
        return None
