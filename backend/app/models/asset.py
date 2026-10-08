from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base
import enum

class AssetType(str, enum.Enum):
    PRODUCTION_PC = "production_pc"
    SERVER = "server"
    SWITCH = "switch"
    ROUTER = "router"
    PRINTER = "printer"
    APPLICATION = "application"
    NETWORK_SERVICE = "network_service"

class AssetStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    MAINTENANCE = "maintenance"

class CriticalityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(100), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), unique=True, nullable=False)
    mac_address = Column(String(17), nullable=True)
    asset_type = Column(Enum(AssetType), nullable=False)
    operating_system = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    production_line = Column(String(100), nullable=True, index=True)
    status = Column(Enum(AssetStatus), default=AssetStatus.ONLINE, nullable=False)
    owner_team = Column(String(100), nullable=True)
    criticality = Column(Enum(CriticalityLevel), default=CriticalityLevel.MEDIUM, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_check = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Asset(hostname='{self.hostname}', ip='{self.ip_address}', status='{self.status}')>"
