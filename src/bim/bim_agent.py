"""
BIM Agent Module
Uses OpenAI to create a specialized assistant for BIM/IFC data
with knowledge of different stakeholder perspectives
"""
import os
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union

# OpenAI import
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.error("OpenAI module not found. Please install it with 'pip install openai'")

from src.bim.mock_ifc import MockIFCObject

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class StakeholderGroup(Enum):
    """Enumeration of real estate stakeholder groups"""
    TENANT_BUYER = "Tenant/Buyer"
    BROKER = "Broker"
    LANDLORD = "Landlord"
    PROPERTY_MANAGER = "Property Manager"
    APPRAISER = "Appraiser"
    MORTGAGE_BROKER = "Mortgage Broker"
    INVESTOR = "Investor"

class BIMAgent:
    """
    BIM Agent using OpenAI
    
    This agent specializes in analyzing BIM data and tailoring responses to different
    real estate stakeholder groups
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the BIM Agent
        
        Args:
            api_key: Optional OpenAI API key (if not provided, will try to get from environment)
        """
        # Check for API key in environment if not provided
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided or found in environment variables")
            self.agent_ready = False
            return
            
        # Initialize the mock BIM data
        self.bim_data = MockIFCObject()
        
        # Create the OpenAI client
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.agent_ready = True
            logger.debug("BIM Agent initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            self.agent_ready = False
    
    def _identify_stakeholder_group(self, query: str) -> StakeholderGroup:
        """
        Identify which stakeholder group the query most likely comes from
        
        Args:
            query: The user's query text
            
        Returns:
            The identified stakeholder group
        """
        # Default to TENANT_BUYER if we can't identify
        default_group = StakeholderGroup.TENANT_BUYER
        
        if not self.agent_ready:
            logger.warning("BIM Agent not ready, using default stakeholder group")
            return default_group
        
        try:
            # Use OpenAI to classify the stakeholder group
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": """
                    You are a classifier that identifies which real estate stakeholder group a query comes from.
                    Categories:
                    - Tenant/Buyer: End users concerned with living experience, costs, amenities
                    - Broker: Sales-focused, interested in marketability, showings, client matching
                    - Landlord: Ownership concerns, long-term value, tenant relations
                    - Property Manager: Day-to-day operations, maintenance, tenant needs
                    - Appraiser: Valuation details, comparable properties, building condition
                    - Mortgage Broker: Financing terms, risk factors, return calculations
                    - Investor: ROI, market trends, appreciation potential, portfolio fit
                    
                    Return just the category name, nothing else.
                    """},
                    {"role": "user", "content": query}
                ],
                temperature=0.0,
                max_tokens=20
            )
            
            # Extract the classification result
            result = response.choices[0].message.content.strip()
            
            # Map the result to a StakeholderGroup enum
            for group in StakeholderGroup:
                if group.value.lower() in result.lower():
                    logger.debug(f"Identified stakeholder group: {group.value}")
                    return group
            
            # If no match is found, return the default
            logger.warning(f"Could not map classification result '{result}' to a stakeholder group, using default")
            return default_group
            
        except Exception as e:
            logger.error(f"Error identifying stakeholder group: {e}")
            return default_group
    
    def process_message(self, query: str) -> Dict[str, Any]:
        """
        Process a message from the user about BIM data
        
        Args:
            query: The user's query
            
        Returns:
            Dictionary containing the response and metadata
        """
        if not self.agent_ready:
            return {
                "error": True,
                "message": "BIM Agent not initialized. Please check your OpenAI API key.",
                "needs_api_key": True
            }
        
        try:
            # Identify the stakeholder group
            stakeholder_group = self._identify_stakeholder_group(query)
            
            # Extract relevant BIM data based on the query
            bim_context = self._extract_relevant_bim_data(query)
            
            # Generate a response tailored to the stakeholder group
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": f"""
                    You are a specialized BIM (Building Information Modeling) assistant for a
                    real estate tokenization platform. Your expertise lies in understanding building models and
                    providing insights tailored to different stakeholder perspectives.
                    
                    The user belongs to the {stakeholder_group.value} stakeholder group. Tailor your
                    response to focus on aspects most relevant to this group.
                    
                    Available building information:
                    {bim_context}
                    
                    Guidelines based on stakeholder:
                    - Tenant/Buyer: Focus on livability, amenities, finishing quality, room layouts
                    - Broker: Emphasize marketable features, comparable properties, unique selling points
                    - Landlord: Highlight maintenance requirements, durability, operating costs
                    - Property Manager: Detail systems accessibility, maintenance schedules, service areas
                    - Appraiser: Provide technical specifications, compliance with standards, quality metrics
                    - Mortgage Broker: Emphasize asset lifespan, risk factors, quality of construction
                    - Investor: Focus on value drivers, performance metrics, sustainability features
                    
                    Keep your responses factual, informative and positive.
                    """},
                    {"role": "user", "content": query}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return {
                "error": False,
                "response": response.choices[0].message.content,
                "stakeholder_group": stakeholder_group.value,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "error": True,
                "message": f"Error processing your request: {str(e)}",
                "query": query
            }
    
    def _extract_relevant_bim_data(self, query: str) -> str:
        """
        Extract relevant BIM data based on the query
        
        Args:
            query: The user's query
            
        Returns:
            A string representation of the relevant BIM data
        """
        # Start with basic project info
        context_data = [
            "Project Information:",
            self._format_dict(self.bim_data.get_project_info()),
            "",
            "Performance Metrics:",
            self._format_dict(self.bim_data.get_performance_metrics()),
            ""
        ]
        
        # Search for query-specific components
        search_terms = [word for word in query.lower().split() if len(word) > 3]
        for term in search_terms:
            results = self.bim_data.search_components(term)
            if results:
                context_data.append(f"\nRelevant components matching '{term}':")
                for item in results:
                    category = item.pop("category", "unknown")
                    context_data.append(f"- {category.capitalize()} component: {self._format_dict(item)}")
        
        # Add specific category data if mentioned in query
        query_lower = query.lower()
        for category in self.bim_data.properties.keys():
            if category in query_lower or category[:-1] in query_lower:  # Check singular form too
                context_data.append(f"\n{category.capitalize()}:")
                for item in self.bim_data.get_property(category):
                    context_data.append(f"- {self._format_dict(item)}")
        
        return "\n".join(context_data)
    
    def _format_dict(self, data: Any) -> str:
        """Format a dictionary as a string with key-value pairs"""
        if not data or not isinstance(data, dict):
            return "No data available"
        return ", ".join([f"{k}: {v}" for k, v in data.items()])


# Create a synchronous wrapper function for the agent
def process_message_sync(query: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Process a message synchronously
    
    Args:
        query: The user's query
        api_key: Optional OpenAI API key
        
    Returns:
        Dictionary containing the response and metadata
    """
    agent = BIMAgent(api_key)
    return agent.process_message(query)