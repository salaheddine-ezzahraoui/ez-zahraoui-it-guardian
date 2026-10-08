# Incident Lifecycle

## Overview

Incidents follow a structured lifecycle from detection to closure.

## State Machine

```
OPEN → INVESTIGATING → IN_PROGRESS → RESOLVED → CLOSED
  ↓         ↓             ↓            ↓
  └─────────┴─────────────┴────────────┘
              (can reopen at any point)
```

## States

### OPEN
- **Created by**: Monitoring engine (auto) or technician (manual)
- **Trigger**: Asset goes OFFLINE, WARNING, or manual creation
- **Auto-assign**: Based on asset criticality (P1/P2/P3/P4)
- **Notification**: Event logged, appears on dashboard

### INVESTIGATING
- **Trigger**: Technician starts analysis
- **Actions**: Review monitoring data, check related assets, run diagnostics
- **AI Assist**: Available via `/api/ai/analyze/{id}`

### IN_PROGRESS
- **Trigger**: Root cause identified, fix in progress
- **Actions**: Apply fix, monitor recovery
- **Assignment**: Must have assigned_technician

### RESOLVED
- **Trigger**: Issue fixed, service restored
- **Auto-resolve**: When asset returns to ONLINE
- **Required**: resolution_notes, root_cause (recommended)
- **Notification**: Event logged

### CLOSED
- **Trigger**: Verification complete, documentation done
- **Actions**: Final review, knowledge base update
- **Cannot reopen**: Must create new incident

## Auto-Creation Rules

| Trigger | Condition | Severity | Priority |
|---------|-----------|----------|----------|
| Asset OFFLINE | Criticality CRITICAL | CRITICAL | P1 |
| Asset OFFLINE | Criticality HIGH | HIGH | P2 |
| Asset OFFLINE | Criticality MEDIUM | MEDIUM | P3 |
| Asset OFFLINE | Criticality LOW | LOW | P4 |
| Asset WARNING | Criticality CRITICAL/HIGH | MEDIUM | P3 |
| Asset RECOVERED | Had active incident | AUTO-RESOLVE | - |

## Duplicate Prevention

System checks for existing active incidents on same asset before creating new one.

```python
# In incident_manager.py
existing = db.query(Incident).filter(
    Incident.asset_id == asset.id,
    Incident.status.in_(['OPEN', 'INVESTIGATING', 'IN_PROGRESS'])
).first()
```

## Escalation Rules

| Priority | Max Time Open | Action |
|----------|---------------|--------|
| P1 | 30 minutes | Event logged, notify on-call |
| P2 | 2 hours | Event logged, notify team lead |
| P3 | 8 hours | Daily review |
| P4 | 24 hours | Weekly review |

## Incident Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| incident_id | String | Auto | Unique ID (INC-XXXX) |
| asset_id | Integer | Yes | FK to assets |
| category | Enum | Yes | NETWORK, SERVER, WORKSTATION, etc. |
| severity | Enum | Yes | LOW, MEDIUM, HIGH, CRITICAL |
| priority | Enum | Yes | P1, P2, P3, P4 |
| status | Enum | Yes | OPEN, INVESTIGATING, IN_PROGRESS, RESOLVED, CLOSED |
| title | String | Yes | Short description |
| description | Text | No | Detailed description |
| detected_at | DateTime | Auto | Creation timestamp |
| resolved_at | DateTime | No | Resolution timestamp |
| assigned_technician | String | No | Technician name |
| root_cause | Text | No | Root cause analysis |
| resolution_notes | Text | No | Resolution details |
| risk_score | Float | No | Calculated risk |
| production_impact | String | No | LOW, MEDIUM, HIGH, CRITICAL |

## Production Impact Assessment

Automatically calculated based on:
- Asset criticality
- Production line association
- Number of affected assets on same line
- Network dependency analysis

## API Operations

### Create Manual Incident
```bash
POST /api/incidents
{
  "asset_id": 42,
  "category": "NETWORK",
  "severity": "HIGH",
  "priority": "P2",
  "title": "Intermittent connectivity",
  "description": "Users reporting drops on Line 3"
}
```

### Assign Technician
```bash
POST /api/incidents/123/assign
{"technician": "Ahmed Z."}
```

### Resolve Incident
```bash
POST /api/incidents/123/resolve
{
  "notes": "Replaced faulty switch port",
  "root_cause": "Bad SFP module on SW-ACCESS-03 port 12"
}
```

### Get Active Incidents
```bash
GET /api/incidents/active
```

## Event Logging

All lifecycle changes create events:
- `INCIDENT_CREATED` - New incident
- `INCIDENT_UPDATED` - Status change, assignment
- `INCIDENT_RESOLVED` - Resolution
- `INCIDENT_ESCALATED` - Escalation triggered

## Dashboard Integration

Active incidents shown on:
- Main dashboard (counts by severity)
- Incident list page
- Asset detail (related incidents)
- Monitoring page (correlated with checks)