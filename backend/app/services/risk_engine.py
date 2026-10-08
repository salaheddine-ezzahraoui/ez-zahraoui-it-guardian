from sqlalchemy.orm import Session
from app.models.asset import Asset, AssetStatus, CriticalityLevel, AssetType
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.monitoring import MonitoringResult
from datetime import datetime, timedelta
from typing import Dict, List

class RiskEngine:
    """
    Transparent IT Risk Scoring Engine
    
    Formula (weights documented):
    - Asset Criticality: 30 points max
    - Availability (offline ratio): 25 points max
    - Network Latency: 15 points max
    - Packet Loss: 15 points max
    - Active Incidents: 15 points max
    Total: 100 points max
    
    Bands:
    0-30: LOW
    31-60: MEDIUM
    61-80: HIGH
    81-100: CRITICAL
    """

    def __init__(self, db: Session):
        self.db = db

    def calculate_asset_risk(self, asset: Asset) -> Dict:
        """Calculate risk score for a single asset"""
        score = 0
        factors = {}

        # 1. Asset Criticality (0-30)
        criticality_scores = {
            CriticalityLevel.CRITICAL: 30,
            CriticalityLevel.HIGH: 20,
            CriticalityLevel.MEDIUM: 10,
            CriticalityLevel.LOW: 5,
        }
        crit_score = criticality_scores.get(asset.criticality, 10)
        score += crit_score
        factors['criticality'] = {
            'value': asset.criticality.value,
            'score': crit_score,
            'weight': 30
        }

        # 2. Availability (0-25)
        if asset.status == AssetStatus.OFFLINE:
            avail_score = 25
        elif asset.status == AssetStatus.WARNING:
            avail_score = 15
        elif asset.status == AssetStatus.MAINTENANCE:
            avail_score = 5
        else:
            avail_score = 0
        score += avail_score
        factors['availability'] = {
            'value': asset.status.value,
            'score': avail_score,
            'weight': 25
        }

        # 3. Network Latency (0-15) - from recent monitoring results
        latency_score = self._calculate_latency_score(asset.id)
        score += latency_score
        factors['latency'] = {
            'score': latency_score,
            'weight': 15
        }

        # 4. Packet Loss (0-15)
        packet_loss_score = self._calculate_packet_loss_score(asset.id)
        score += packet_loss_score
        factors['packet_loss'] = {
            'score': packet_loss_score,
            'weight': 15
        }

        # 5. Active Incidents (0-15)
        incident_score = self._calculate_incident_score(asset.id)
        score += incident_score
        factors['incidents'] = {
            'score': incident_score,
            'weight': 15
        }

        # Cap at 100
        final_score = min(score, 100)
        band = self._get_band(final_score)

        return {
            'asset_id': asset.id,
            'hostname': asset.hostname,
            'risk_score': final_score,
            'risk_band': band,
            'factors': factors,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def _calculate_latency_score(self, asset_id: int) -> int:
        """Calculate latency score from recent ICMP results"""
        recent = self.db.query(MonitoringResult).filter(
            MonitoringResult.asset_id == asset_id,
            MonitoringResult.check_type == 'ICMP',
            MonitoringResult.result == 'SUCCESS',
            MonitoringResult.response_time_ms.isnot(None),
            MonitoringResult.checked_at > datetime.utcnow() - timedelta(hours=1)
        ).all()

        if not recent:
            return 0

        avg_latency = sum(r.response_time_ms for r in recent) / len(recent)

        if avg_latency > 200:
            return 15
        elif avg_latency > 100:
            return 10
        elif avg_latency > 50:
            return 5
        else:
            return 0

    def _calculate_packet_loss_score(self, asset_id: int) -> int:
        """Calculate packet loss score from recent ICMP results"""
        recent = self.db.query(MonitoringResult).filter(
            MonitoringResult.asset_id == asset_id,
            MonitoringResult.check_type == 'ICMP',
            MonitoringResult.packet_loss_percent.isnot(None),
            MonitoringResult.checked_at > datetime.utcnow() - timedelta(hours=1)
        ).all()

        if not recent:
            return 0

        avg_loss = sum(r.packet_loss_percent for r in recent) / len(recent)

        if avg_loss > 20:
            return 15
        elif avg_loss > 10:
            return 10
        elif avg_loss > 5:
            return 5
        else:
            return 0

    def _calculate_incident_score(self, asset_id: int) -> int:
        """Calculate score based on active incidents"""
        active = self.db.query(Incident).filter(
            Incident.asset_id == asset_id,
            Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.INVESTIGATING, IncidentStatus.IN_PROGRESS])
        ).all()

        if not active:
            return 0

        severity_weights = {
            IncidentSeverity.CRITICAL: 5,
            IncidentSeverity.HIGH: 4,
            IncidentSeverity.MEDIUM: 2,
            IncidentSeverity.LOW: 1,
        }

        total = sum(severity_weights.get(i.severity, 1) for i in active)
        return min(total, 15)

    def _get_band(self, score: int) -> str:
        if score <= 30:
            return "LOW"
        elif score <= 60:
            return "MEDIUM"
        elif score <= 80:
            return "HIGH"
        else:
            return "CRITICAL"

    def calculate_overall_risk(self) -> Dict:
        """Calculate overall infrastructure risk"""
        assets = self.db.query(Asset).filter(Asset.is_active == True).all()
        if not assets:
            return {'risk_score': 0, 'risk_band': 'LOW', 'assets': []}

        asset_risks = [self.calculate_asset_risk(a) for a in assets]
        total_score = sum(r['risk_score'] for r in asset_risks)
        avg_score = int(total_score / len(assets))
        band = self._get_band(avg_score)

        return {
            'risk_score': avg_score,
            'risk_band': band,
            'total_assets': len(assets),
            'assets': asset_risks,
            'calculated_at': datetime.utcnow().isoformat()
        }

    def get_risk_breakdown(self) -> Dict:
        """Get risk score breakdown by category"""
        assets = self.db.query(Asset).filter(Asset.is_active == True).all()
        if not assets:
            return {}

        breakdown = {
            'criticality': {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0},
            'availability': {'ONLINE': 0, 'OFFLINE': 0, 'WARNING': 0, 'MAINTENANCE': 0},
            'by_band': {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        }

        for asset in assets:
            risk = self.calculate_asset_risk(asset)
            breakdown['criticality'][asset.criticality.value] += 1
            breakdown['availability'][asset.status.value] += 1
            breakdown['by_band'][risk['risk_band']] += 1

        return breakdown