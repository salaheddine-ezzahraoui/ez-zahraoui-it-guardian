# EZ-ZAHRAOUI IT Guardian

**IT Production Monitoring, Incident Management & Infrastructure Intelligence Platform**

A containerized internal IT operations platform for monitoring infrastructure assets, detecting availability issues, managing incidents, and assessing potential production impact in industrial/automotive production environments.

## Features

### Infrastructure Inventory
- Register and track 83+ assets (Production PCs, Servers, Switches, Routers, Printers, Applications, Network Services)
- Rich metadata: hostname, IP, MAC, type, OS, location, production line, criticality, owner team

### Automated Monitoring
- **ICMP Ping**: Concurrent checks every 60s (20 parallel workers)
- **TCP Port Checks**: Critical ports on servers (22, 80, 443, 3389, 5432, 8080)
- **HTTP Health**: Web application endpoints
- All results stored in PostgreSQL with history

### Incident Management
- **Auto-creation**: When assets go offline/degraded
- **Severity/Priority**: Based on asset criticality (P1-P4)
- **Lifecycle**: Open → Investigating → In Progress → Resolved → Closed
- **Technician Assignment**: Track ownership
- **Escalation**: Time-based rules

### Production Impact
- Correlate incidents with production lines
- Calculate health per production line
- Identify affected assets and criticality

### IT Risk Scoring
- Transparent formula (0-100)
- Factors: Criticality, Availability, Latency, Packet Loss, Incidents
- Bands: LOW (0-30), MEDIUM (31-60), HIGH (61-80), CRITICAL (81-100)

### Operations Dashboard
- Real-time health scores (production, infrastructure, network, servers)
- Asset status cards (online/warning/offline)
- Incident counts by severity
- Production line health
- Recent events timeline

### AI-Assisted Troubleshooting (Optional)
- Local LLM via Ollama
- Structured output: Observed Facts / Possible Causes / Recommended Steps
- Clear disclaimer: hypotheses, not confirmed diagnoses

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, PostgreSQL |
| Frontend | React 18, TypeScript, Vite, Heroicons |
| Monitoring | Python asyncio, custom workers |
| Database | PostgreSQL 16 |
| Reverse Proxy | Nginx |
| AI | Ollama (local LLM) |
| Containerization | Docker, Docker Compose |
| Cloud | Azure ready (Container Apps, PostgreSQL Flexible) |

## Quick Start

```bash
# Clone
git clone <repo>
cd ez-zahraoui-it-guardian

# Configure
cp .env.example .env
# Edit .env with your values

# Start
docker-compose up -d

# Access
# Dashboard: http://localhost:3000
# API Docs:  http://localhost:8000/docs
```

## Project Structure

```
ez-zahraoui-it-guardian/
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   ├── routers/   # API endpoints
│   │   └── services/  # Business logic
│   └── Dockerfile
├── frontend/          # React dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── Dockerfile
├── monitoring/        # Monitoring engine
│   ├── workers/       # ICMP, TCP, HTTP workers
│   └── Dockerfile
├── infrastructure/    # Nginx, Prometheus, Grafana configs
├── docker/            # Docker entrypoints
├── docs/              # Documentation
├── docker-compose.yml
├── .env.example
├── .gitignore
└── LICENSE
```

## Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Monitoring
![Monitoring](docs/screenshots/monitoring.png)

## API Documentation

See [API.md](docs/API.md) for complete endpoint reference.

Key endpoints:
- `GET /api/dashboard/stats` - Real-time dashboard data
- `GET /api/assets` - List all assets
- `GET /api/incidents` - Incident management
- `GET /api/monitoring/results` - Monitoring history
- `GET /api/risk/overall` - Risk scoring
- `GET /api/ai/analyze/{id}` - AI troubleshooting

## Deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Docker Compose (local/production)
- Linux/Ubuntu manual deployment
- Azure Container Apps deployment
- Systemd service setup
- Backup/restore procedures

## Security

See [SECURITY.md](docs/SECURITY.md) for:
- Current security posture
- Production hardening checklist
- Threat model
- Compliance notes

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Reference](docs/API.md)
- [Risk Scoring](docs/RISK_SCORING.md)
- [Incident Lifecycle](docs/INCIDENT_LIFECYCLE.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Security](docs/SECURITY.md)

## CV / Portfolio Description

> **EZ-ZAHRAOUI IT Guardian** — IT Production Monitoring & Incident Management Platform
>
> Developed a containerized IT operations platform for monitoring infrastructure assets, detecting availability issues, managing incidents and assessing potential production impact. Implemented automated health checks (ICMP/TCP/HTTP), REST APIs with FastAPI, PostgreSQL persistence, real-time React dashboard, transparent risk scoring, and AI-assisted troubleshooting. Deployed via Docker Compose with Nginx reverse proxy, ready for Azure Container Apps.

## License

MIT License - see [LICENSE](LICENSE)

## Author

**EZ-ZAHRAOUI IT SERVICES**

Built for portfolio demonstration of IT Operations, DevOps, and Cloud Engineering skills.