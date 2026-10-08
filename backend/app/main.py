from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import health, dashboard, incidents, monitoring, risk, ai

app = FastAPI(
    title="EZ-ZAHRAOUI IT Guardian",
    description="IT Production Monitoring, Incident Management & Infrastructure Intelligence Platform",
    version="0.1.0",
)

# CORS - allows React frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(dashboard.router, tags=["Dashboard"])
app.include_router(incidents.router, tags=["Incidents"])
app.include_router(monitoring.router, tags=["Monitoring"])
app.include_router(risk.router, tags=["Risk"])
app.include_router(ai.router, tags=["AI"])

@app.get("/")
def root():
    return {
        "message": "EZ-ZAHRAOUI IT Guardian API",
        "version": "0.1.0",
        "status": "running"
    }