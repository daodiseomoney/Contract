import os

class Config:
    SECRET_KEY = os.environ.get("SESSION_SECRET", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # IPFS config
    IPFS_HOST = "localhost"
    IPFS_PORT = 5001
    
    # Cosmos config
    COSMOS_CHAIN_ID = "cosmoshub-4"
    COSMOS_LCD_URL = "https://lcd-cosmoshub.keplr.app"
    
    # LLM config
    LLM_MODEL = "distilbert-base-uncased"
    MAX_TOKENS = 512
    
    # BIMserver config
    BIMSERVER_URL = os.environ.get("BIMSERVER_URL", "http://localhost:8080")
    BIMSERVER_USERNAME = os.environ.get("BIMSERVER_USERNAME", "admin@example.com")
    BIMSERVER_PASSWORD = os.environ.get("BIMSERVER_PASSWORD", "admin")
    BIMSERVER_ENABLED = os.environ.get("BIMSERVER_ENABLED", "False") == "True"
