"""Application configuration loaded from environment variables."""
from __future__ import annotations

import os
from typing import List

from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Application
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:4173"

    # Database
    database_url: str = "sqlite+aiosqlite:///./safezone.db"

    # MQTT
    mqtt_broker_host: str = "localhost"
    mqtt_broker_port: int = 1883
    mqtt_topic_incidents: str = "safezone/incidents"
    mqtt_topic_status: str = "safezone/status"
    mqtt_username: str = ""
    mqtt_password: str = ""  # never logged
    mqtt_client_id: str = "safezone-backend"

    # Perception
    perception_adapter: str = "simulated"  # "simulated" | "pipegen" | "deepstream"
    pipegen_output_dir: str = "./pipegen_output"
    detection_confidence_threshold: float = 0.5
    incident_cooldown_seconds: int = 5

    # Logging
    log_level: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
