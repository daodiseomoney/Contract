"""
BIM Agent module for the BIM AI Management Dashboard.
This module provides AI capabilities for processing BIM data and interacting with users.
"""

import logging
import os
from typing import Dict, List, Optional, Tuple, Union

from src.bim.bim_agent_openai import OpenAIBIMAgent
from src.bim.mock_ifc import MockIFCData

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BIMAgentManager:
    """
    BIM Agent Manager for handling AI interactions and BIM data
    This is the main entry point for the BIM AI functionality
    """
    
    def __init__(self):
        """Initialize the BIM Agent Manager"""
        self.openai_agent = OpenAIBIMAgent()
        self.mock_ifc_data = MockIFCData()
        self.enhanced_mode_enabled = False
        self.api_key_available = os.environ.get("OPENAI_API_KEY") is not None
        
        if not self.api_key_available:
            logger.warning("OPENAI_API_KEY not found in environment variables")
    
    def toggle_enhanced_mode(self, enabled: bool = True) -> Dict:
        """
        Toggle between standard and enhanced AI modes
        Returns API response with status and mode
        """
        if enabled and not self.api_key_available:
            return {
                "success": False,
                "enhanced_mode": False,
                "message": "OpenAI API key not available. Enhanced mode requires a valid API key."
            }
        
        try:
            self.enhanced_mode_enabled = self.openai_agent.toggle_enhanced_mode(enabled)
            return {
                "success": True,
                "enhanced_mode": self.enhanced_mode_enabled,
                "message": f"Enhanced mode {'enabled' if self.enhanced_mode_enabled else 'disabled'}"
            }
        except Exception as e:
            logger.error(f"Error toggling enhanced mode: {e}")
            return {
                "success": False,
                "enhanced_mode": self.enhanced_mode_enabled,
                "message": f"Error toggling enhanced mode: {str(e)}"
            }
    
    def get_enhanced_mode(self) -> bool:
        """Get the current enhanced mode status"""
        return self.enhanced_mode_enabled
    
    def process_message(self, message: str) -> Dict:
        """
        Process a message from the user
        Returns API response with AI message and metadata
        """
        if not message or not message.strip():
            return {
                "success": False,
                "message": "Message cannot be empty",
                "response": None,
                "metadata": {}
            }
        
        # Get BIM data for context
        bim_data = {
            "summary": self.mock_ifc_data.get_building_summary(),
            "elements": self.mock_ifc_data.get_all_elements()[:3]  # Limit to first 3 elements
        }
        
        try:
            # Process message with OpenAI agent
            response, metadata = self.openai_agent.process_message(message, bim_data)
            
            return {
                "success": True,
                "message": "Successfully processed message",
                "response": response,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "message": f"Error processing message: {str(e)}",
                "response": "Sorry, I encountered an error processing your message. Please try again.",
                "metadata": {"error": str(e)}
            }
    
    def get_building_data(self) -> Dict:
        """Get building data for the UI"""
        return {
            "building": self.mock_ifc_data.get_building_summary(),
            "spaces": self.mock_ifc_data.get_spaces(),
            "elements_sample": self.mock_ifc_data.get_all_elements()[:5]
        }
    
    def get_element_by_id(self, element_id: str) -> Dict:
        """Get element details by ID"""
        element = self.mock_ifc_data.get_element_by_id(element_id)
        if element:
            return {
                "success": True,
                "element": element
            }
        else:
            return {
                "success": False,
                "message": f"Element with ID {element_id} not found"
            }
