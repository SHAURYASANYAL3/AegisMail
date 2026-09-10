from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    app_name: str = "AegisMail Platform"
    app_version: str = "1.0.0"
    env: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"
    
    # Offline / Demo Mode Guarantee
    demo_mode: bool = True
    
    # Database
    database_url: str = "sqlite:///./aegismail.db"
    
    # Evidence file storage
    evidence_storage_dir: str = "./backend/data/cases"
    
    # Security
    secret_key: str = "dev_secret_key_aegismail_dfir_2026"
    allowed_origins: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # Optional External Threat Intel (0 required for MVP)
    vt_api_key: str = ""
    abuseipdb_api_key: str = ""
    urlscan_api_key: str = ""
    
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()
os.makedirs(settings.evidence_storage_dir, exist_ok=True)
