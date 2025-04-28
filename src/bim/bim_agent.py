"""
BIM Agent module for the BIM AI Management Dashboard.
This module provides AI capabilities for processing BIM data and interacting with users.
"""

import logging
import os
from typing import Dict, Optional, List
import glob

from src.bim.bim_agent_openai import OpenAIBIMAgent
from src.bim.mock_ifc import MockIFCData
from src.bim.ifc_parser import IFCParser
from src.bim.ifc_agent import IFCAgent

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
        
        # Initialize the IFC Agent with OpenAI Agents SDK
        self.ifc_agent = IFCAgent()
        
        # Default to mock data
        self.use_real_ifc = False
        self.mock_ifc_data = MockIFCData()
        
        # Initialize IFC parser but don't load any file yet
        self.ifc_parser = IFCParser()
        self.current_ifc_file = None

        # Try to find IFC files in the uploads directory
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
        
        # Create uploads directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # OpenAI API integration
        self.enhanced_mode_enabled = False
        self.api_key_available = os.environ.get("OPENAI_API_KEY") is not None

        if not self.api_key_available:
            logger.warning("OPENAI_API_KEY not found in environment variables")
            
        # Try to load the first available IFC file
        self._load_first_available_ifc()

    def _load_first_available_ifc(self) -> bool:
        """
        Try to load the first available IFC file in the uploads directory.
        
        Returns:
            bool: True if a file was loaded, False otherwise
        """
        try:
            # Find all IFC files in the uploads directory
            ifc_files = glob.glob(os.path.join(self.upload_dir, "*.ifc"))
            
            if ifc_files:
                # Sort by modification time (newest first)
                ifc_files.sort(key=os.path.getmtime, reverse=True)
                
                # Try to load the newest file
                if self.ifc_parser.load_file(ifc_files[0]):
                    self.current_ifc_file = ifc_files[0]
                    self.use_real_ifc = True
                    logger.info(f"Loaded IFC file: {os.path.basename(ifc_files[0])}")
                    return True
            
            logger.info("No IFC files found in uploads directory, using mock data")
            return False
        
        except Exception as e:
            logger.error(f"Error loading IFC file: {str(e)}")
            return False
    
    def load_ifc_file(self, file_path: str) -> Dict:
        """
        Load a specific IFC file.
        
        Args:
            file_path: Path to the IFC file
            
        Returns:
            Dict: Response with success/failure status
        """
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"File not found: {file_path}",
            }
        
        try:
            if self.ifc_parser.load_file(file_path):
                self.current_ifc_file = file_path
                self.use_real_ifc = True
                
                return {
                    "success": True,
                    "message": f"Successfully loaded IFC file: {os.path.basename(file_path)}",
                }
            else:
                return {
                    "success": False,
                    "message": f"Failed to load IFC file: {os.path.basename(file_path)}",
                }
        except Exception as e:
            logger.error(f"Error loading IFC file: {str(e)}")
            return {
                "success": False,
                "message": f"Error loading IFC file: {str(e)}",
            }

    def toggle_enhanced_mode(self, enabled: bool = True) -> Dict:
        """
        Toggle between standard and enhanced AI modes
        Returns API response with status and mode
        """
        if enabled and not self.api_key_available:
            return {
                "success": False,
                "enhanced_mode": False,
                "message": "OpenAI API key not available. Enhanced mode requires a valid API key.",
            }

        try:
            self.enhanced_mode_enabled = self.openai_agent.toggle_enhanced_mode(enabled)
            return {
                "success": True,
                "enhanced_mode": self.enhanced_mode_enabled,
                "message": f"Enhanced mode {'enabled' if self.enhanced_mode_enabled else 'disabled'}",
            }
        except Exception as e:
            logger.error(f"Error toggling enhanced mode: {e}")
            return {
                "success": False,
                "enhanced_mode": self.enhanced_mode_enabled,
                "message": f"Error toggling enhanced mode: {str(e)}",
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
                "metadata": {},
            }

        # Get BIM data for context (either real or mock)
        if self.use_real_ifc and self.current_ifc_file:
            bim_data = {
                "summary": self.ifc_parser.get_building_summary(),
                "elements": self.ifc_parser.get_all_elements()[:3],  # Limit to first 3 elements
            }
        else:
            bim_data = {
                "summary": self.mock_ifc_data.get_building_summary(),
                "elements": self.mock_ifc_data.get_all_elements()[:3],
            }

        try:
            # Process message with OpenAI agent
            response, metadata = self.openai_agent.process_message(message, bim_data)

            return {
                "success": True,
                "message": "Successfully processed message",
                "response": response,
                "metadata": metadata,
            }
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "message": f"Error processing message: {str(e)}",
                "response": "Sorry, I encountered an error processing your message. Please try again.",
                "metadata": {"error": str(e)},
            }

    def get_building_data(self) -> Dict:
        """Get building data for the UI"""
        if self.use_real_ifc and self.current_ifc_file:
            # Get data from real IFC file
            return {
                "building": self.ifc_parser.get_building_summary(),
                "spaces": self.ifc_parser.get_spaces(),
                "elements_sample": self.ifc_parser.get_all_elements()[:5],
                "using_real_ifc": True,
                "ifc_file": os.path.basename(self.current_ifc_file) if self.current_ifc_file else None,
            }
        else:
            # Fall back to mock data
            return {
                "building": self.mock_ifc_data.get_building_summary(),
                "spaces": self.mock_ifc_data.get_spaces(),
                "elements_sample": self.mock_ifc_data.get_all_elements()[:5],
                "using_real_ifc": False,
                "ifc_file": None,
            }

    def get_element_by_id(self, element_id: str) -> Dict:
        """Get element details by ID"""
        if self.use_real_ifc and self.current_ifc_file:
            element = self.ifc_parser.get_element_by_id(element_id)
        else:
            element = self.mock_ifc_data.get_element_by_id(element_id)
            
        if element:
            return {"success": True, "element": element}
        else:
            return {
                "success": False,
                "message": f"Element with ID {element_id} not found",
            }
    
    def get_element_types(self) -> List[str]:
        """Get all element types in the loaded IFC file"""
        if self.use_real_ifc and self.current_ifc_file:
            return self.ifc_parser.get_element_types()
        else:
            # Create a simulation of element types from mock data
            element_types = set()
            for element in self.mock_ifc_data.get_all_elements():
                if "type" in element:
                    element_types.add(element["type"])
            return sorted(list(element_types))
    
    def get_elements_by_type(self, element_type: str) -> List[Dict]:
        """Get all elements of a specific type"""
        if self.use_real_ifc and self.current_ifc_file:
            return self.ifc_parser.get_elements_by_type(element_type)
        else:
            # Filter mock data
            return [
                element for element in self.mock_ifc_data.get_all_elements() 
                if element.get("type") == element_type
            ]
