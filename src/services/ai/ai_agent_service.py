"""
AI Agent Service for integrating OpenAI with BIM data.
This service handles AI capabilities and integrations for BIM analysis.
"""

import os
import logging
from typing import Dict, List, Optional
import openai

from src.entities.stakeholder import StakeholderGroup
from src.gateways.ifc.ifc_gateway import IFCGateway

# Configure logging
logger = logging.getLogger(__name__)

class AIAgentService:
    """
    AI Agent Service for integrating OpenAI with BIM data.
    This service provides AI-enhanced analysis of BIM data.
    """
    
    def __init__(self):
        """Initialize the AI Agent Service"""
        self.client = None
        
        try:
            self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
    
    def analyze_ifc_file(self, file_path: str) -> Dict:
        """
        Analyze an IFC file using AI.
        
        Args:
            file_path: Path to the IFC file
            
        Returns:
            Dict: Analysis results with metadata
        """
        if not self.client:
            return {
                "success": False,
                "message": "OpenAI client not available",
                "metadata": {"error": "api_unavailable"}
            }
        
        try:
            # Load IFC file using gateway
            gateway = IFCGateway(file_path)
            
            # Get summary information
            summary = gateway.summary()
            
            # If unable to get summary, return error
            if not summary.get("success", False):
                return {
                    "success": False,
                    "message": summary.get("message", "Failed to analyze IFC file"),
                    "metadata": {"error": "ifc_load_error"}
                }
            
            # Prepare context for AI analysis
            element_types = gateway.get_element_types()
            elements_count = summary.get("elements", 0)
            schema = summary.get("schema", "Unknown")
            site_name = summary.get("site_name", "Unknown")
            
            # Call OpenAI API for AI analysis
            analysis_prompt = (
                f"Analyze this building:\n"
                f"- File schema: {schema}\n"
                f"- Site name: {site_name}\n"
                f"- Total elements: {elements_count}\n"
                f"- Element types: {', '.join(element_types)}\n\n"
                f"Provide a professional analysis including:\n"
                f"1. Building complexity assessment\n"
                f"2. Key architectural features\n"
                f"3. Recommendations for stakeholders\n"
                f"Keep the analysis concise and professional."
            )
            
            # Create the completion
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert BIM analyst."},
                    {"role": "user", "content": analysis_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            analysis_text = response.choices[0].message.content
            
            # Create structured results
            result = {
                "success": True,
                "message": "IFC file analyzed successfully",
                "analysis": analysis_text,
                "metadata": {
                    "file_path": file_path,
                    "schema": schema,
                    "site_name": site_name,
                    "elements_count": elements_count,
                    "element_types": element_types
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing IFC file: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "metadata": {"error": "analysis_error"}
            }
    
    def get_ifc_summary(self, file_path: str) -> Dict:
        """
        Get a quick summary of an IFC file.
        
        Args:
            file_path: Path to the IFC file
            
        Returns:
            Dict: Summary information
        """
        try:
            gateway = IFCGateway(file_path)
            summary = gateway.summary()
            
            if not summary.get("success", False):
                return {
                    "success": False,
                    "message": summary.get("message", "Failed to load IFC file")
                }
            
            return {
                "success": True,
                "summary": {
                    "elements": summary.get("elements", 0),
                    "schema": summary.get("schema", "Unknown"),
                    "site_name": summary.get("site_name", "Unknown")
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting IFC summary: {e}")
            return {
                "success": False,
                "message": f"Error: {str(e)}"
            }
    
    def identify_stakeholder(self, messages: List[Dict]) -> Optional[str]:
        """
        Identify which stakeholder group a user belongs to based on their messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Optional[str]: Stakeholder group identifier or None if not identified
        """
        if not self.client:
            logger.error("Cannot identify stakeholder: OpenAI client not available")
            return None
            
        try:
            # Extract user messages
            user_text = " ".join(
                [msg["content"] for msg in messages if msg["role"] == "user"]
            )
            
            if not user_text:
                return None
                
            # Prepare system message for stakeholder identification
            system_message = (
                "Identify which of the following real estate stakeholder groups the person belongs to "
                "based on their messages: Tenant/Buyer, Broker, Landlord, "
                "Property Manager, Appraiser, Mortgage Broker, or Investor. "
                "Return only the stakeholder type as a single word or phrase."
            )
            
            # Call OpenAI API for stakeholder identification
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=20,
                temperature=0.1
            )
            
            stakeholder_text = response.choices[0].message.content.strip().lower()
            
            # Map the returned text to our stakeholder groups
            mapping = {
                "tenant": StakeholderGroup.TENANT_BUYER,
                "buyer": StakeholderGroup.TENANT_BUYER,
                "tenant/buyer": StakeholderGroup.TENANT_BUYER,
                "broker": StakeholderGroup.BROKER,
                "landlord": StakeholderGroup.LANDLORD,
                "property manager": StakeholderGroup.PROPERTY_MANAGER,
                "appraiser": StakeholderGroup.APPRAISER,
                "mortgage broker": StakeholderGroup.MORTGAGE_BROKER,
                "investor": StakeholderGroup.INVESTOR
            }
            
            # Find the closest match
            for key, value in mapping.items():
                if key in stakeholder_text:
                    logger.debug(f"Identified stakeholder: {value}")
                    return value
                    
            # Default to investor if no match found
            return StakeholderGroup.INVESTOR
            
        except Exception as e:
            logger.error(f"Error identifying stakeholder: {e}")
            return None