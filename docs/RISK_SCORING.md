# Risk Scoring Documentation

## Overview

The IT Risk Score is a transparent, documented calculation that provides a single number (0-100) representing the current risk level of your IT infrastructure.

## Formula

```
Risk Score = Criticality + Availability + Latency + Packet Loss + Incidents
            (0-30)    +    (0-25)    +    (0-15)   +     (0-15)     +  (0-15)
                      = 100 max
```

## Factor Details

### 1. Asset Criticality (0-30 points)
Based on the asset's business importance.

| Criticality | Score | Description |
|-------------|-------|-------------|
| CRITICAL    | 30    | Core infrastructure (core routers, AD, DB) |
| HIGH        | 20    | Production systems (servers, production PCs) |
| MEDIUM      | 10    | Supporting systems (access switches, printers) |
| LOW         | 5     | Non-critical (office printers, test systems) |

### 2. Availability (0-25 points)
Based on current asset status from monitoring.

| Status | Score | Description |
|--------|-------|-------------|
| OFFLINE | 25 | Asset not responding to checks |
| WARNING | 15 | Degraded (packet loss, high latency) |
| MAINTENANCE | 5 | Planned maintenance |
| ONLINE | 0 | Healthy |

### 3. Network Latency (0-15 points)
Average ICMP response time over last hour.

| Avg Latency | Score |
|-------------|-------|
| > 200ms     | 15    |
| 100-200ms   | 10    |
| 50-100ms    | 5     |
| < 50ms      | 0     |

### 4. Packet Loss (0-15 points)
Average ICMP packet loss over last hour.

| Avg Packet Loss | Score |
|-----------------|-------|
| > 20%           | 15    |
| 10-20%          | 10    |
| 5-10%           | 5     |
| < 5%            | 0     |

### 5. Active Incidents (0-15 points)
Based on open incidents for this asset.

| Severity | Weight per Incident |
|----------|---------------------|
| CRITICAL | 5 |
| HIGH     | 4 |
| MEDIUM   | 2 |
| LOW      | 1 |

Max 15 points (capped).

## Risk Bands

| Score | Band | Color | Action |
|-------|------|-------|--------|
| 0-30  | LOW  | 🟢 Green | Normal operations, routine monitoring |
| 31-60 | MEDIUM | 🟡 Yellow | Increased attention, review warnings |
| 61-80 | HIGH | 🟠 Orange | Active investigation required |
| 81-100 | CRITICAL | 🔴 Red | Immediate action, escalate to management |

## Examples

### Example 1: Healthy Production PC
- Criticality: HIGH (20)
- Status: ONLINE (0)
- Latency: 18ms (0)
- Packet Loss: 0% (0)
- Incidents: None (0)
- **Total: 20 → LOW**

### Example 2: Degraded Server
- Criticality: CRITICAL (30)
- Status: WARNING (15)
- Latency: 150ms (10)
- Packet Loss: 8% (5)
- Incidents: 1 HIGH (4)
- **Total: 64 → HIGH**

### Example 3: Offline Core Router
- Criticality: CRITICAL (30)
- Status: OFFLINE (25)
- Latency: N/A (15 - max since no data)
- Packet Loss: 100% (15)
- Incidents: 1 CRITICAL (5)
- **Total: 90 → CRITICAL**

## Overall Infrastructure Risk

The overall risk is the **average** of all asset risk scores:

```
Overall Risk = Σ(Asset Risk Scores) / Total Assets
```

This provides a single number for executive dashboards.

## Configuration

All weights are in `backend/app/services/risk_engine.py` and can be adjusted.

## Transparency

The calculation is:
- **Deterministic**: Same inputs always produce same output
- **Auditable**: Each factor shown in API response
- **No ML**: No black-box models, just documented rules
- **Explainable**: Each point traceable to a specific factor