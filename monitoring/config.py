import os
from dotenv import load_dotenv

load_dotenv()

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://guardian:guardian_password@localhost:5432/it_guardian")

# Monitoring settings
MONITORING_INTERVAL_SECONDS = int(os.getenv("MONITORING_INTERVAL_SECONDS", "60"))
MONITORING_TIMEOUT_SECONDS = int(os.getenv("MONITORING_TIMEOUT_SECONDS", "5"))
MONITORING_PING_COUNT = int(os.getenv("MONITORING_PING_COUNT", "4"))

# TCP ports to check on servers
TCP_PORTS = {
    "server": [22, 80, 443, 3389, 5432, 8080],
    "network_service": [53, 80, 443, 8080],
    "application": [80, 443, 8080],
}

# HTTP health check endpoints
HTTP_ENDPOINTS = {
    "application": "/health",
    "network_service": "/",
}
