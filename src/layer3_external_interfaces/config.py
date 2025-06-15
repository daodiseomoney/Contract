"""
Configuration module for DAODISEO Platform
Provides centralized configuration management
"""

import os
from typing import Dict, Any

class Config:
    """Application configuration class"""
    
    # Database configuration
    DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://localhost/daodiseo")
    
    # API Keys and secrets
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-key")
    
    # Blockchain configuration
    RPC_URL = "https://testnet-rpc.daodiseo.chaintools.tech"
    CHAIN_ID = "ithaca-1"
    
    # Application settings
    DEBUG = os.environ.get("DEBUG", "True").lower() == "true"
    PORT = int(os.environ.get("PORT", 5000))
    HOST = os.environ.get("HOST", "0.0.0.0")
    
    # BIM server configuration
    BIMSERVER_ENABLED = os.environ.get("BIMSERVER_ENABLED", "False").lower() == "true"
    BIMSERVER_URL = os.environ.get("BIMSERVER_URL", "http://localhost:8080")
    
    # File upload settings
    MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = "uploads"
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get all configuration as dictionary"""
        return {
            "database_url": cls.DATABASE_URL,
            "debug": cls.DEBUG,
            "port": cls.PORT,
            "host": cls.HOST,
            "rpc_url": cls.RPC_URL,
            "chain_id": cls.CHAIN_ID,
            "bimserver_enabled": cls.BIMSERVER_ENABLED,
            "has_openai_key": bool(cls.OPENAI_API_KEY)
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate required configuration"""
        required_vars = ["SESSION_SECRET"]
        
        for var in required_vars:
            if not getattr(cls, var, None):
                return False
        
        return True