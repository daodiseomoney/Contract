"""
Unified AI Service - Consolidated AI functionality for BIM analysis
Combines OpenAI BIM Agent, IFC Agent, and AI Agent Service into a single module
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from src.layer1_entities.stakeholder import StakeholderGroup
from src.layer2_interface_adapters.gateways.ifc.ifc_gateway import IFCGateway

# Configure logging
logger = logging.getLogger(__name__)


class UnifiedAIService:
    """
    Unified AI service combining all AI functionality for BIM analysis
    Consolidates OpenAI BIM Agent, IFC Agent, and general AI services
    """

    def __init__(self):
        """Initialize the Unified AI Service"""
        self.client = None
        self.enhanced_mode = False
        self.identified_stakeholder = None
        self.conversation_history = []
        self.bim_data = None
        self.ifc_file = None
        self.ifc_gateway = IFCGateway()
        self.openai_agents_available = False
        
        # Set up paths
        self.upload_dir = os.path.join(os.getcwd(), "uploads")
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir)

        # Initialize OpenAI client
        try:
            import openai
            self.client = openai.OpenAI()
            logger.debug("OpenAI client initialized successfully")
        except (ImportError, Exception) as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            self.client = None

        # Check for OpenAI Agents SDK
        try:
            import openai_agents
            self.openai_agents_available = True
        except ImportError:
            logger.warning("Limited functionality due to missing openai-agents dependency")
            self.openai_agents_available = False

    def toggle_enhanced_mode(self, enabled: bool = True) -> bool:
        """Toggle between standard and enhanced AI modes"""
        self.enhanced_mode = enabled
        logger.info(f"Enhanced mode {'enabled' if enabled else 'disabled'}")
        return self.enhanced_mode

    def identify_stakeholder(self, messages: List[Dict]) -> Optional[str]:
        """Identify stakeholder group based on user messages"""
        if not self.client:
            logger.error("Cannot identify stakeholder: OpenAI client not available")
            return None

        try:
            # Extract text from messages for analysis
            text_content = " ".join([msg.get('content', '') for msg in messages[-3:]])
            
            # Stakeholder identification patterns
            stakeholder_patterns = {
                StakeholderGroup.LANDLORD: ['property', 'rent', 'tenant', 'lease', 'income'],
                StakeholderGroup.ARCHITECT: ['design', 'blueprint', 'structure', 'plan'],
                StakeholderGroup.CONTRACTOR: ['construction', 'build', 'materials', 'labor'],
                StakeholderGroup.INVESTOR: ['investment', 'return', 'profit', 'portfolio'],
                StakeholderGroup.BROKER: ['sale', 'commission', 'client', 'market']
            }

            # Simple pattern matching for stakeholder identification
            for stakeholder, keywords in stakeholder_patterns.items():
                if any(keyword in text_content.lower() for keyword in keywords):
                    self.identified_stakeholder = stakeholder
                    logger.info(f"Identified stakeholder: {stakeholder}")
                    return stakeholder.value

            return None
        except Exception as e:
            logger.error(f"Error identifying stakeholder: {e}")
            return None

    def load_ifc_file(self, file_path: str) -> bool:
        """Load an IFC file for AI processing"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"IFC file not found: {file_path}")
                return False

            # Use IFC gateway to load file
            self.ifc_file = self.ifc_gateway.load_ifc_file(file_path)
            if self.ifc_file:
                logger.info(f"Successfully loaded IFC file: {file_path}")
                return True
            else:
                logger.error(f"Failed to load IFC file: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error loading IFC file: {e}")
            return False

    def analyze_bim_data(self, ifc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze BIM data and provide AI insights"""
        if not self.client:
            return {"error": "OpenAI client not available"}

        try:
            # Extract key metrics from IFC data
            element_count = len(ifc_data.get('elements', []))
            building_info = ifc_data.get('building_info', {})
            
            # Generate analysis based on data
            analysis = {
                "complexity_score": min(element_count / 1000, 1.0),
                "quality_score": 0.8,  # Base quality score
                "sustainability_score": 0.7,  # Base sustainability score
                "cost_efficiency_score": 0.75,  # Base cost efficiency
                "detected_issues": [],
                "recommendations": [
                    "Consider energy-efficient materials",
                    "Optimize structural design for cost savings",
                    "Implement sustainable building practices"
                ]
            }

            if element_count < 100:
                analysis["detected_issues"].append("Low detail level in BIM model")
            if element_count > 5000:
                analysis["detected_issues"].append("High complexity may impact construction timeline")

            return analysis
        except Exception as e:
            logger.error(f"Error analyzing BIM data: {e}")
            return {"error": str(e)}

    def process_user_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process user query with AI assistance"""
        if not self.client:
            return "AI service not available. Please check configuration."

        try:
            # Build context for the query
            system_prompt = "You are a BIM AI assistant helping with real estate tokenization."
            
            if self.identified_stakeholder:
                system_prompt += f" The user is identified as a {self.identified_stakeholder}."
            
            if context and context.get('bim_data'):
                system_prompt += " BIM data is available for analysis."

            # Simple response generation (placeholder for actual OpenAI call)
            return f"Based on your query about: {query[:100]}..., I recommend consulting the BIM data analysis results."
            
        except Exception as e:
            logger.error(f"Error processing user query: {e}")
            return "Error processing your query. Please try again."

    def get_stakeholder_specific_insights(self) -> List[str]:
        """Get insights specific to identified stakeholder"""
        if not self.identified_stakeholder:
            return ["General BIM analysis insights available"]

        stakeholder_insights = {
            StakeholderGroup.LANDLORD: [
                "Property maintenance cost optimization opportunities",
                "Rental income potential analysis",
                "Energy efficiency improvements for cost reduction"
            ],
            StakeholderGroup.ARCHITECT: [
                "Structural design optimization suggestions",
                "Material selection recommendations",
                "Code compliance verification"
            ],
            StakeholderGroup.CONTRACTOR: [
                "Construction sequencing optimization",
                "Material quantity estimations",
                "Cost reduction opportunities"
            ],
            StakeholderGroup.INVESTOR: [
                "ROI potential analysis",
                "Market value projections",
                "Risk assessment factors"
            ],
            StakeholderGroup.BROKER: [
                "Market positioning strategies",
                "Competitive advantage features",
                "Buyer attraction points"
            ]
        }

        return stakeholder_insights.get(self.identified_stakeholder, [])