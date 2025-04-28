"""
BIM Agent service for the BIM AI Management Dashboard.
This module provides AI capabilities for processing BIM data and interacting with users.
"""

import logging
import os
from typing import Dict, List

from src.services.ai.bim_agent_openai import OpenAIBIMAgent
from src.services.ai.ifc_agent import IFCAgent
from src.gateways.ifc.ifc_gateway import IFCGateway
from src.services.ai.ai_agent_service import AIAgentService

# Configure logging
logger = logging.getLogger(__name__)


class BIMAgentManager:
    """
    BIM Agent Manager for handling AI interactions and BIM data.
    This is the main entry point for the BIM AI functionality.
    """

    def __init__(self):
        """Initialize the BIM Agent Manager"""
        # Initialize components
        self.ifc_gateway = IFCGateway()
        self.bim_agent = OpenAIBIMAgent()
        self.ifc_agent = IFCAgent()
        self.ai_service = AIAgentService()
        
        # Set up paths
        self.upload_dir = os.path.join(os.getcwd(), "uploads")
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)
            
        # Try to load a default IFC file if available
        self._load_first_available_ifc()
        
    def _load_first_available_ifc(self) -> bool:
        """
        Try to load the first available IFC file in the uploads directory.

        Returns:
            bool: True if a file was loaded, False otherwise
        """
        try:
            # Check if uploads directory exists
            if not os.path.exists(self.upload_dir):
                logger.warning(f"Uploads directory not found: {self.upload_dir}")
                return False
                
            # Look for .ifc files
            ifc_files = []
            for file in os.listdir(self.upload_dir):
                if file.lower().endswith(".ifc"):
                    ifc_files.append(os.path.join(self.upload_dir, file))
                    
            if not ifc_files:
                logger.warning("No IFC files found in uploads directory.")
                return False
                
            # Load the first file
            file_path = ifc_files[0]
            success = self.load_ifc_file(file_path)
            if success:
                logger.info(f"Loaded IFC file: {os.path.basename(file_path)}")
            return success
            
        except Exception as e:
            logger.error(f"Error loading default IFC file: {e}")
            return False
            
    def load_ifc_file(self, file_path: str) -> Dict:
        """
        Load a specific IFC file.

        Args:
            file_path: Path to the IFC file

        Returns:
            Dict: Response with success/failure status
        """
        try:
            # Load file using IFC gateway
            gateway_success = self.ifc_gateway.load_file(file_path)
            if not gateway_success:
                return {
                    "success": False,
                    "message": "Failed to parse IFC file"
                }
                
            # Also load into IFC agent
            agent_success = self.ifc_agent.load_ifc_file(file_path)
            
            # Get summary
            summary = self.ifc_gateway.summary()
            
            # Do an AI analysis of the IFC file
            analysis = self.ai_service.analyze_ifc_file(file_path)
            
            return {
                "success": True,
                "message": f"Successfully loaded {os.path.basename(file_path)}",
                "building": summary,
                "agent_enabled": agent_success,
                "analysis": analysis.get("analysis", "")
            }
            
        except Exception as e:
            logger.error(f"Error loading IFC file: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
            
    def toggle_enhanced_mode(self, enabled: bool = True) -> Dict:
        """
        Toggle between standard and enhanced AI modes.
        Returns API response with status and mode.
        """
        try:
            mode_enabled = self.bim_agent.toggle_enhanced_mode(enabled)
            return {
                "success": True,
                "enhanced_mode": mode_enabled
            }
        except Exception as e:
            logger.error(f"Error toggling enhanced mode: {e}")
            return {
                "success": False,
                "message": str(e)
            }
            
    def get_enhanced_mode(self) -> bool:
        """Get the current enhanced mode status"""
        return self.bim_agent.enhanced_mode
        
    def process_message(self, message: str) -> Dict:
        """
        Process a message from the user.
        Returns API response with AI message and metadata.
        """
        try:
            # Get BIM data for context if available
            bim_data = None
            if self.ifc_gateway.model:
                summary = self.ifc_gateway.summary()
                bim_data = {
                    "summary": summary,
                    "element_count": summary.get("elements", 0)
                }
                
            # Process with BIM agent
            response_text, metadata = self.bim_agent.process_message(message, bim_data)
            
            # For enhanced mode, optionally add IFC agent insights
            if self.bim_agent.enhanced_mode and self.ifc_agent.ifc_file and "filtered" not in metadata:
                try:
                    # Only use IFC agent if message is specifically about the building/BIM data
                    bim_keywords = ["building", "model", "ifc", "bim", "element", "wall", "floor", 
                                   "door", "window", "column", "beam", "slab", "space", "material"]
                    
                    if any(keyword in message.lower() for keyword in bim_keywords):
                        ifc_response = self.ifc_agent.process_query(message)
                        if ifc_response["success"]:
                            metadata["ifc_agent"] = {
                                "analysis": True,
                                "agent_based": ifc_response.get("metadata", {}).get("agent_based", False)
                            }
                except Exception as e:
                    logger.warning(f"IFC Agent analysis failed: {e}")
                    
            return {
                "success": True,
                "message": response_text,
                "metadata": metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
            
    def get_building_data(self) -> Dict:
        """Get building data for the UI"""
        if not self.ifc_parser.ifc_file:
            return {
                "success": False,
                "message": "No IFC file loaded"
            }
            
        try:
            building_summary = self.ifc_parser.get_building_summary()
            element_types = self.ifc_parser.get_element_types()
            element_counts = {}
            
            for element_type in element_types:
                elements = self.ifc_parser.get_elements_by_type(element_type)
                element_counts[element_type] = len(elements)
                
            return {
                "success": True,
                "building": building_summary,
                "element_types": element_types,
                "element_counts": element_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting building data: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
            
    def get_element_by_id(self, element_id: str) -> Dict:
        """Get element details by ID"""
        if not self.ifc_parser.ifc_file:
            return {
                "success": False,
                "message": "No IFC file loaded"
            }
            
        try:
            element = self.ifc_parser.get_element_by_id(element_id)
            if not element:
                return {
                    "success": False,
                    "message": f"Element with ID {element_id} not found"
                }
                
            return {
                "success": True,
                "element": element
            }
            
        except Exception as e:
            logger.error(f"Error getting element: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
            
    def get_element_types(self) -> List[str]:
        """Get all element types in the loaded IFC file"""
        if not self.ifc_parser.ifc_file:
            return []
            
        return self.ifc_parser.get_element_types()
        
    def get_elements_by_type(self, element_type: str) -> List[Dict]:
        """Get all elements of a specific type"""
        if not self.ifc_parser.ifc_file:
            return []
            
        return self.ifc_parser.get_elements_by_type(element_type)