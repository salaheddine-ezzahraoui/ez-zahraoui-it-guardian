# API Reference

## Base URL

```
Development: http://localhost:8000
Production:  https://your-domain.com/api
```

## Authentication

Currently no authentication required (internal tool).
Add JWT authentication for production use.

## Endpoints

### Health

#### GET /health
Health check endpoint for load balancers.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-10-08T19:51:57.046756Z",
  "service": "ez-zahraoui-it-guardian"
}
```

### Dashboard

#### GET /api/dashboard/stats
Real-time dashboard statistics.

**Response:**
```json
{
  "total_assets": 83,
  "online_assets": 28,
  "offline_assets": 38,
  "warning_assets": 17,
  "maintenance_assets": 0,
  "active_incidents": 10,
  "critical_incidents": 1,
  "high_incidents": 3,
  "medium_incidents": 6,
  "low_incidents": 0,
  "overall_health": 66,
  "production_health": 66,
  "network_health": 75,
  "server_health": 80,
  "risk_score": 40,
  "risk_band": "MEDIUM"
}
```

#### GET /api/production-lines
Production line health breakdown.

**Response:**
```json
[
  {
    "line": "Line 1",
    "total": 11,
    "online": 7,
    "offline": 3,
    "warning": 1,
    "health": 63
  }
]
```

#### GET /api/events
Recent system events.

**Response:**
```json
[
  {
    "id": 1,
    "event_type": "MONITORING_CHECK",
    "message": "PROD-PC-024 is OFFLINE (ping timeout)",
    "created_at": "2026-10-08T19:51:57.046756Z"
  }
]
```

### Assets

#### GET /api/assets
List all assets.

**Query Parameters:**
- `skip` (int, default 0)
- `limit` (int, default 100)

**Response:**
```json
[
  {
    "id": 1,
    "hostname": "PROD-PC-001",
    "ip_address": "192.168.10.1",
    "mac_address": "00:1A:2B:3C:01:01",
    "asset_type": "production_pc",
    "operating_system": "Windows 10 IoT Enterprise",
    "location": "Workshop A",
    "production_line": "Line 1",
    "status": "online",
    "owner_team": "Production IT",
    "criticality": "high",
    "description": "Production workstation 1",
    "is_active": true,
    "last_check": "2026-10-08T19:51:57.046756Z",
    "created_at": "2026-10-08T18:09:44.603393Z",
    "updated_at": "2026-10-08T18:09:44.603393Z"
  }
]
```

### Incidents

#### GET /api/incidents
List incidents with filters.

**Query Parameters:**
- `status` (string): open, investigating, in_progress, resolved, closed
- `severity` (string): low, medium, high, critical
- `skip` (int, default 0)
- `limit` (int, default 100)

#### GET /api/incidents/active
Get all active incidents.

#### GET /api/incidents/{incident_id}
Get single incident details.

#### PATCH /api/incidents/{incident_id}
Update incident.

**Request Body:**
```json
{
  "status": "in_progress",
  "assigned_technician": "Ahmed Z.",
  "resolution_notes": "Investigating switch port",
  "root_cause": "Faulty SFP module"
}
```

#### POST /api/incidents/{incident_id}/assign
Assign technician.

**Request Body:**
```json
{
  "technician": "Ahmed Z."
}
```

#### POST /api/incidents/{incident_id}/resolve
Resolve incident.

**Request Body:**
```json
{
  "notes": "Replaced SFP module, connectivity restored",
  "root_cause": "Faulty SFP module on SW-ACCESS-03 port 12"
}
```

#### POST /api/incidents/escalate
Escalate stale incidents.

### Monitoring

#### GET /api/monitoring/results
List monitoring results.

**Query Parameters:**
- `check_type` (string): icmp, tcp, http
- `result` (string): success, failure, timeout, error
- `asset_id` (int)
- `limit` (int, default 50)
- `skip` (int, default 0)

#### GET /api/monitoring/summary
Monitoring summary statistics.

**Response:**
```json
{
  "breakdown": {
    "icmp": {"success": 45, "timeout": 38},
    "tcp": {"success": 102, "failure": 0},
    "http": {"success": 0, "failure": 9}
  },
  "average_response_time_ms": 18.5,
  "checks_last_24h": 1247
}
```

### Risk Scoring

#### GET /api/risk/overall
Overall infrastructure risk.

**Response:**
```json
{
  "risk_score": 40,
  "risk_band": "MEDIUM",
  "total_assets": 83,
  "assets": [
    {
      "asset_id": 1,
      "hostname": "PROD-PC-001",
      "risk_score": 15,
      "risk_band": "LOW",
      "factors": {
        "criticality": {"value": "high", "score": 20, "weight": 30},
        "availability": {"value": "online", "score": 0, "weight": 25},
        "latency": {"score": 0, "weight": 15},
        "packet_loss": {"score": 0, "weight": 15},
        "incidents": {"score": 0, "weight": 15}
      }
    }
  ]
}
```

#### GET /api/risk/asset/{asset_id}
Risk for specific asset.

#### GET /api/risk/breakdown
Risk distribution breakdown.

#### GET /api/risk/all
All asset risks.

### AI Troubleshooting

#### GET /api/ai/analyze/{incident_id}
AI analysis of incident.

**Response:**
```json
{
  "incident_id": "INC-1042",
  "asset": {
    "hostname": "PROD-PC-024",
    "ip": "192.168.10.24",
    "type": "production_pc",
    "criticality": "high",
    "production_line": "Line 2"
  },
  "observed_facts": [
    "ICMP ping failing for PROD-PC-024 (3 recent failures)",
    "High average latency: 240ms",
    "Packet loss detected: 18.0% average"
  ],
  "possible_causes": [
    {
      "cause": "Network connectivity loss to host",
      "likelihood": "high",
      "reasoning": "ICMP timeout indicates host unreachable or firewall blocking"
    },
    {
      "cause": "Network congestion or link degradation",
      "likelihood": "high",
      "reasoning": "Packet loss typically indicates link issues"
    }
  ],
  "recommended_steps": [
    {
      "step": 1,
      "action": "Verify PROD-PC-024 power and OS status",
      "command": "ping 192.168.10.24",
      "priority": "immediate"
    },
    {
      "step": 2,
      "action": "Check upstream switch port status",
      "command": "show interface status",
      "priority": "immediate"
    },
    {
      "step": 3,
      "action": "Run extended ping test to measure loss pattern",
      "command": "ping -n 50 192.168.10.24",
      "priority": "immediate"
    }
  ],
  "confidence": "medium",
  "disclaimer": "This analysis is generated by AI based on available monitoring data. It represents hypotheses, not confirmed diagnoses. Always verify before taking action.",
  "generated_at": "2026-10-08T19:51:57.046756Z"
}
```

#### GET /api/ai/health
AI service health.

## Error Responses

All errors follow this format:
```json
{
  "detail": "Error message"
}
```

Common HTTP codes:
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error