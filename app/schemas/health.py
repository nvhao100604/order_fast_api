from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class DatabaseHealth(BaseModel):
    status: str = Field(description="Database connection status: 'connected' or 'disconnected'")
    latency_ms: Optional[float] = Field(default=None, description="Query execution latency in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if disconnected")

class HealthCheckResponse(BaseModel):
    status: str = Field(description="Overall service status: 'healthy' or 'unhealthy'")
    timestamp: datetime = Field(description="Current timestamp in ISO format")
    environment: str = Field(description="Current runtime environment (e.g. development, production)")
    database: DatabaseHealth = Field(description="Database health details")

