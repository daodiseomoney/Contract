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
