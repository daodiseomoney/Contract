"""
BIM model entities for the Real Estate Tokenization Platform.
Defines the core domain objects related to Building Information Modeling.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any


@dataclass
class BIMElement:
    """Represents a single element in a BIM model"""
    id: str
    element_type: str
    properties: Dict[str, Any]
    geometry: Optional[Dict[str, Any]] = None
    

@dataclass
class BIMModel:
    """Represents a complete BIM model"""
    id: str
    filename: str
    file_path: str
    file_hash: Optional[str] = None
    summary: Optional[Dict[str, Any]] = None
    elements: Optional[List[BIMElement]] = None
    creation_date: datetime = datetime.utcnow()
    

@dataclass
class AIAssistantMessage:
    """Represents a message in a conversation with the BIM AI assistant"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = datetime.utcnow()
    metadata: Optional[Dict[str, Any]] = None