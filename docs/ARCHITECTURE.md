# Architecture Documentation

## Overview

EZ-ZAHRAOUI IT Guardian is a containerized IT production monitoring and incident management platform designed for industrial/automotive production environments.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION INFRASTRUCTURE                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │PROD-PC-001│ │PROD-PC-024│ │SRV-AD-01  │ │SW-ACCESS-03│       │
│  └─────┬────┘ └─────┬────┘ └─────┬────┘ └─────┬────┘          │
└────────┼─────────────┼─────────────┼─────────────┼──────────────┘
         │             │             │             │
         ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MONITORING ENGINE                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ ICMP Worker  │ │ TCP Worker   │ │ HTTP Worker  │               │
│  │ (ping)       │ │ (port check) │ │ (health)     │               │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘               │
│         └────────────────┼────────────────┘                     │
│                          ▼                                      │
│              ┌───────────────────────┐                          │
│              │   Monitoring Service   │                          │
│              │   (Python asyncio)     │                          │
│              └───────────┬───────────┘                          │
└──────────────────────────┼──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │  Asset    │ │Incident  │ │Monitoring│ │Dashboard │          │
│  │  API      │ │API       │ │API       │ │API       │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                        │
│  │  Risk     │ │Production│ │AI Tshoot │                        │
│  │  Engine   │ │Impact    │ │Engine    │                        │
│  └──────────┘ └──────────┘ └──────────┘                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
┌──────────────────┐ ┌───────────┐ ┌───────────┐
│   PostgreSQL     │ │ Prometheus│ │  Ollama   │
│   (Database)     │ │ (Metrics) │ │  (LLM)    │
└──────────────────┘ └───────────┘ └───────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     Grafana      │
                  └─────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     REACT FRONTEND                               │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              Operations Dashboard                         │    │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐      │    │
│  │  │Overview │ │ Assets  │ │Incidents│ │Monitoring│      │    │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘      │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Production Infrastructure
- **Production PCs**: 45 industrial workstations running HMI/SCADA
- **Servers**: 8 servers (AD, ERP, MES, File, Backup, DB, Web, Monitoring)
- **Network**: 12 switches, 4 routers, 2 firewalls
- **Services**: DNS, DHCP, NTP, LDAP, HTTP applications

### 2. Monitoring Engine (Python asyncio)
- **ICMP Worker**: Concurrent ping checks (20 parallel)
- **TCP Worker**: Port availability checks (10 parallel)
- **HTTP Worker**: Health endpoint checks (10 parallel)
- **Interval**: Configurable (default 60s)
- **Storage**: All results in PostgreSQL

### 3. FastAPI Backend
- **Framework**: FastAPI 0.115+ with async support
- **Database**: SQLAlchemy 2.0 + PostgreSQL
- **API Endpoints**:
  - `/api/dashboard/stats` - Real-time dashboard metrics
  - `/api/assets` - Asset CRUD
  - `/api/incidents` - Incident management
  - `/api/monitoring/results` - Monitoring history
  - `/api/risk/overall` - Risk scoring
  - `/api/ai/analyze/{id}` - AI troubleshooting

### 4. PostgreSQL Database
- **Tables**: assets, incidents, monitoring_results, events
- **Enums**: Asset types, statuses, incident categories, severities
- **Indexes**: Optimized for dashboard queries

### 5. React Frontend
- **Framework**: React 18 + TypeScript + Vite
- **UI**: Custom dark theme with Heroicons
- **Pages**: Dashboard, Monitoring, Assets, Incidents
- **Real-time**: 15s auto-refresh

### 6. AI Troubleshooting (Optional)
- **LLM**: Ollama (local) with llama3.2
- **Input**: Incident + monitoring context
- **Output**: Facts / Causes / Steps (structured JSON)

## Data Flow

1. **Monitoring Cycle** (every 60s):
   - Engine reads active assets from PostgreSQL
   - Workers execute ICMP/TCP/HTTP checks concurrently
   - Results saved to `monitoring_results`
   - Asset status updated in `assets`
   - Events logged to `events`
   - Incidents auto-created for state changes

2. **Dashboard Query**:
   - Frontend polls `/api/dashboard/stats` every 15s
   - Backend queries PostgreSQL aggregates
   - Returns JSON with health scores, counts, risk

3. **Incident Lifecycle**:
   - Auto-created on asset status change (ONLINE → OFFLINE)
   - Severity based on asset criticality
   - Technician assigned via API
   - Resolved manually or auto on recovery

## Security

- No secrets in code (`.env` files)
- CORS configured for frontend origin
- Database credentials via environment variables
- Nginx reverse proxy with security headers
- HTTPS ready (certificate configuration needed)

## Deployment

See `DEPLOYMENT.md` for Docker and Linux deployment instructions.