"""
Consolidated AI Orchestrator for DAODISEO Platform
Combines all orchestrator functionality including o3-mini, chain brain, and agent orchestration
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from openai import OpenAI

logger = logging.getLogger(__name__)

@dataclass
class TaskResult:
    """Result of an orchestrated task"""
    success: bool
    response: str
    task_id: str
    metadata: Dict[str, Any]
    reasoning_steps: List[str]
    metrics: Dict[str, Any]
    error: Optional[str] = None

class ConsolidatedAIOrchestrator:
    """Unified AI orchestrator handling all AI coordination tasks"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.is_running = True
        self.task_history = []
        
    def orchestrate_task(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main orchestration method for any AI task"""
        try:
            task_id = f"task-{int(time.time())}-{hash(task) % 10000}"
            
            # Determine task type and route appropriately
            if context.get("request_chain_analysis"):
                return self._handle_chain_analysis_task(task, context, task_id)
            elif context.get("source") == "bim_ai_assistant_with_chain_brain":
                return self._handle_bim_task(task, context, task_id)
            elif "token" in task.lower() or "metrics" in task.lower():
                return self._handle_token_analysis(task, context, task_id)
            elif "staking" in task.lower() or "validator" in task.lower():
                return self._handle_staking_analysis(task, context, task_id)
            else:
                return self._handle_general_task(task, context, task_id)
                
        except Exception as e:
            logger.error(f"Orchestration error: {e}")
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "response": "Orchestration failed"
            }
    
    def _handle_chain_analysis_task(self, task: str, context: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Handle blockchain data analysis tasks"""
        try:
            prompt = f"""
            Analyze the following blockchain-related request with deep technical insight:
            
            Task: {task}
            Context: {json.dumps(context, indent=2)}
            
            Provide comprehensive analysis including:
            - Technical assessment of blockchain metrics
            - Market implications
            - Risk factors
            - Strategic recommendations
            - Performance indicators
            
            Return detailed analysis with specific metrics and actionable insights.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a blockchain analyst with expertise in Cosmos ecosystem, tokenomics, and DeFi protocols. Provide detailed technical analysis with specific metrics and recommendations."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "response": analysis,
                "task_id": task_id,
                "metadata": {
                    "agent_type": "chain_brain_orchestrator",
                    "enhanced_mode": True,
                    "analysis_type": "blockchain"
                },
                "reasoning_steps": [
                    "Analyzed blockchain context",
                    "Applied technical assessment",
                    "Generated strategic recommendations"
                ],
                "metrics": {
                    "analysis_depth": "comprehensive",
                    "confidence": 0.9
                }
            }
            
        except Exception as e:
            logger.error(f"Chain analysis error: {e}")
            return {"success": False, "error": str(e), "task_id": task_id}
    
    def _handle_bim_task(self, task: str, context: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Handle BIM and property analysis tasks"""
        try:
            prompt = f"""
            Analyze this Building Information Modeling (BIM) and real estate request:
            
            Task: {task}
            Stakeholder Type: {context.get('stakeholder_type', 'general')}
            
            Provide detailed analysis covering:
            - Property assessment and valuation insights
            - Tokenization opportunities
            - Investment potential
            - Risk factors
            - Technical BIM analysis if applicable
            - Market positioning recommendations
            
            Focus on actionable insights for real estate tokenization and investment.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a real estate and BIM specialist with expertise in property tokenization, investment analysis, and blockchain-based real estate platforms."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "response": analysis,
                "task_id": task_id,
                "metadata": {
                    "agent_type": "bim_property_analyst",
                    "enhanced_mode": True,
                    "analysis_type": "property"
                },
                "reasoning_steps": [
                    "Analyzed property context",
                    "Assessed tokenization potential",
                    "Generated investment recommendations"
                ],
                "metrics": {
                    "analysis_type": "property_bim",
                    "confidence": 0.85
                }
            }
            
        except Exception as e:
            logger.error(f"BIM task error: {e}")
            return {"success": False, "error": str(e), "task_id": task_id}
    
    def _handle_token_analysis(self, task: str, context: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Handle token metrics and analysis"""
        blockchain_data = context.get("blockchain_data", {})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a DeFi analyst specializing in token economics and blockchain metrics analysis."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze token metrics for ODIS token on Cosmos Odiseo testnet. Data: {json.dumps(blockchain_data, indent=2)}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "data": analysis,
                "task_id": task_id
            }
            
        except Exception as e:
            logger.error(f"Token analysis error: {e}")
            return {"success": False, "error": str(e), "task_id": task_id}
    
    def _handle_staking_analysis(self, task: str, context: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Handle staking metrics and validator analysis"""
        validators_data = context.get("validators_data", {})
        network_data = context.get("network_data", {})
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a Proof-of-Stake blockchain analyst with expertise in validator performance and staking economics."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze staking metrics and validator performance. Validators: {json.dumps(validators_data, indent=2)} Network: {json.dumps(network_data, indent=2)}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "data": analysis,
                "task_id": task_id
            }
            
        except Exception as e:
            logger.error(f"Staking analysis error: {e}")
            return {"success": False, "error": str(e), "task_id": task_id}
    
    def _handle_general_task(self, task: str, context: Dict[str, Any], task_id: str) -> Dict[str, Any]:
        """Handle general AI tasks"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant for the DAODISEO real estate tokenization platform. Provide helpful and accurate responses."
                    },
                    {
                        "role": "user",
                        "content": task
                    }
                ],
                temperature=0.3
            )
            
            return {
                "success": True,
                "response": response.choices[0].message.content,
                "task_id": task_id,
                "metadata": {
                    "agent_type": "general_assistant",
                    "analysis_type": "general"
                }
            }
            
        except Exception as e:
            logger.error(f"General task error: {e}")
            return {"success": False, "error": str(e), "task_id": task_id}
    
    def analyze_token_metrics(self, blockchain_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze token metrics using AI"""
        return self._handle_token_analysis("token metrics analysis", {"blockchain_data": blockchain_data}, f"token-{int(time.time())}")
    
    def analyze_staking_metrics(self, validators_data: Dict[str, Any], network_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze staking metrics using AI"""
        return self._handle_staking_analysis(
            "staking metrics analysis", 
            {"validators_data": validators_data, "network_data": network_data}, 
            f"staking-{int(time.time())}"
        )
    
    def analyze_network_health(self, rpc_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze network health using AI"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a blockchain network analyst specializing in network health and performance monitoring."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze network health and performance. Data: {json.dumps(rpc_data, indent=2)}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            return {
                "success": True,
                "data": analysis
            }
            
        except Exception as e:
            logger.error(f"Network health analysis error: {e}")
            return {"success": False, "error": str(e)}


class ChainBrainService:
    """Consolidated chain brain service for blockchain data integration"""
    
    def __init__(self):
        self.is_running = False
        self.data_cache = {}
        self.last_update = 0
    
    def start(self):
        """Start the chain brain service"""
        self.is_running = True
        logger.info("Chain brain service started")
    
    def stop(self):
        """Stop the chain brain service"""
        self.is_running = False
        logger.info("Chain brain service stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status"""
        return {
            "running": self.is_running,
            "last_update": self.last_update,
            "cache_size": len(self.data_cache)
        }

# Global instances
_orchestrator_instance = None
_chain_brain_service_instance = None

def get_orchestrator() -> ConsolidatedAIOrchestrator:
    """Get singleton orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = ConsolidatedAIOrchestrator()
    return _orchestrator_instance

def get_chain_brain_service() -> ChainBrainService:
    """Get singleton chain brain service instance"""
    global _chain_brain_service_instance
    if _chain_brain_service_instance is None:
        _chain_brain_service_instance = ChainBrainService()
    return _chain_brain_service_instance

def get_chain_brain_orchestrator():
    """Compatibility function for existing code"""
    return get_orchestrator()

# Compatibility class for existing DaodiseoAgentsOrchestrator usage
class DaodiseoAgentsOrchestrator:
    """Compatibility wrapper for consolidated orchestrator"""
    
    def __init__(self):
        self.orchestrator = get_orchestrator()
    
    def analyze_token_metrics(self, blockchain_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.orchestrator.analyze_token_metrics(blockchain_data)
    
    def analyze_staking_metrics(self, validators_data: Dict[str, Any], network_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.orchestrator.analyze_staking_metrics(validators_data, network_data)
    
    def analyze_network_health(self, rpc_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.orchestrator.analyze_network_health(rpc_data)