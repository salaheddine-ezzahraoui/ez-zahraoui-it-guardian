from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class CheckType(str, enum.Enum):
    ICMP = "icmp"
    TCP = "tcp"
    HTTP = "http"

class CheckResult(str, enum.Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"

class MonitoringResult(Base):
    __tablename__ = "monitoring_results"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), nullable=False)
    check_type = Column(Enum(CheckType), nullable=False)
    result = Column(Enum(CheckResult), nullable=False)
    response_time_ms = Column(Float, nullable=True)
    packet_loss_percent = Column(Float, nullable=True)
    status_code = Column(Integer, nullable=True)
    message = Column(String(500), nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    asset = relationship("Asset", backref="monitoring_results")

    def __repr__(self):
        return f"<MonitoringResult(asset_id={self.asset_id}, check='{self.check_type}', result='{self.result}')>"
