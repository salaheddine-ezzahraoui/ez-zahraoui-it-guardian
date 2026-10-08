# Deployment Guide

## Prerequisites

- Docker 24+ and Docker Compose 2.20+
- Git
- 4GB+ RAM available
- Ports 80, 443, 3000, 5432, 8000 available

## Quick Start (Docker Compose)

```bash
# Clone repository
git clone <your-repo>
cd ez-zahraoui-it-guardian

# Copy environment template
cp .env.example .env

# Edit .env with your values
nano .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Environment Variables

Create `.env` from `.env.example`:

```env
# Database
DATABASE_URL=postgresql://guardian:your_secure_password@postgres:5432/it_guardian
POSTGRES_USER=guardian
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=it_guardian

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_DEBUG=false
SECRET_KEY=your_very_long_random_secret_key_here

# Monitoring
MONITORING_INTERVAL_SECONDS=60
MONITORING_TIMEOUT_SECONDS=5
MONITORING_PING_COUNT=4

# Frontend
VITE_API_URL=http://your-domain.com/api

# AI (Optional)
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2
```

## Manual Deployment (Linux/Ubuntu)

### 1. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo apt install docker-compose-plugin

# Install PostgreSQL client (for local DB)
sudo apt install postgresql-client
```

### 2. Setup Application

```bash
# Clone
git clone <your-repo>
cd ez-zahraoui-it-guardian

# Create .env
cp .env.example .env
# Edit .env with production values

# Build and start
docker-compose -f docker-compose.yml up -d --build
```

### 3. Initialize Database

```bash
# Run migrations (if using Alembic)
docker-compose exec backend python init_db.py

# Or run seed data
docker-compose exec backend python seed_data.py
```

### 4. Configure Nginx (Production)

```bash
# Create SSL certificates (Let's Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Copy to nginx ssl directory
sudo mkdir -p infrastructure/nginx/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem infrastructure/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem infrastructure/nginx/ssl/key.pem

# Restart nginx
docker-compose restart nginx
```

### 5. Systemd Service (Optional)

Create `/etc/systemd/system/it-guardian.service`:

```ini
[Unit]
Description=EZ-ZAHRAOUI IT Guardian
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/ez-zahraoui-it-guardian
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable it-guardian
sudo systemctl start it-guardian
```

## Azure Deployment

### Prerequisites
- Azure CLI installed and logged in
- Azure subscription

### Steps

```bash
# Create resource group
az group create --name rg-it-guardian --location westeurope

# Create container registry
az acr create --resource-group rg-it-guardian --name itguardianacr --sku Basic

# Build and push images
az acr build --registry itguardianacr --image backend ./backend
az acr build --registry itguardianacr --image frontend ./frontend
az acr build --registry itguardianacr --image monitoring ./monitoring

# Create PostgreSQL Flexible Server
az postgres flexible-server create \
  --resource-group rg-it-guardian \
  --name it-guardian-db \
  --location westeurope \
  --admin-user guardian \
  --admin-password YourSecurePassword123 \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32

# Create Container Apps Environment
az containerapp env create \
  --name it-guardian-env \
  --resource-group rg-it-guardian \
  --location westeurope

# Deploy backend
az containerapp create \
  --name it-guardian-backend \
  --resource-group rg-it-guardian \
  --environment it-guardian-env \
  --image itguardianacr.azurecr.io/backend:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars DATABASE_URL=postgresql://guardian:YourSecurePassword123@it-guardian-db.postgres.database.azure.com:5432/it_guardian

# Deploy frontend
az containerapp create \
  --name it-guardian-frontend \
  --resource-group rg-it-guardian \
  --environment it-guardian-env \
  --image itguardianacr.azurecr.io/frontend:latest \
  --target-port 3000 \
  --ingress external \
  --env-vars VITE_API_URL=https://it-guardian-backend.xxx.azurecontainerapps.io

# Deploy monitoring
az containerapp create \
  --name it-guardian-monitoring \
  --resource-group rg-it-guardian \
  --environment it-guardian-env \
  --image itguardianacr.azurecr.io/monitoring:latest \
  --env-vars DATABASE_URL=postgresql://guardian:YourSecurePassword123@it-guardian-db.postgres.database.azure.com:5432/it_guardian
```

## Monitoring & Maintenance

### Health Checks

```bash
# Check all services
docker-compose ps

# Check backend health
curl http://localhost:8000/health

# Check database
docker-compose exec postgres pg_isready -U guardian

# Check monitoring engine logs
docker-compose logs -f monitoring
```

### Backup Database

```bash
# Create backup
docker-compose exec postgres pg_dump -U guardian it_guardian > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T postgres psql -U guardian it_guardian < backup_20240101.sql
```

### Update Application

```bash
git pull
docker-compose build --no-cache
docker-compose up -d
```

### Log Rotation

Configure Docker logging in `docker-compose.yml`:

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Troubleshooting

### Backend won't start
```bash
docker-compose logs backend
# Check DATABASE_URL in .env
# Ensure postgres is healthy first
```

### Frontend can't reach API
```bash
# Check CORS settings in backend/main.py
# Verify VITE_API_URL in .env
# Check nginx proxy configuration
```

### Monitoring engine not creating incidents
```bash
docker-compose logs monitoring
# Check asset statuses in database
# Verify incident creation logic
```

## Security Checklist

- [ ] Change default PostgreSQL password
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS with valid certificates
- [ ] Configure firewall (only 80/443 open)
- [ ] Set up fail2ban for SSH
- [ ] Regular security updates: `apt update && apt upgrade`
- [ ] Monitor Docker images for vulnerabilities: `docker scan`