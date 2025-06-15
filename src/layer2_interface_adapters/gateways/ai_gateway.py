"""
AI Gateway - Clean Architecture Layer 2
Gateway interface and implementation for AI services (OpenAI)
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import os
import openai


class AIGatewayInterface(ABC):
    """Abstract interface for AI gateway"""
    
    @abstractmethod
    def analyze_bim_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze BIM model using AI"""
        pass


class AIGateway(AIGatewayInterface):
    """Implementation of AI gateway using OpenAI"""
    
    def __init__(self):
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
    
    def analyze_bim_model(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze BIM model using OpenAI API
        
        Args:
            model_data: Dictionary containing BIM model information
            
        Returns:
            Analysis results from AI
        """
        try:
            if not self.api_key:
                return self._fallback_analysis(model_data)
            
            # Prepare prompt for AI analysis
            prompt = self._create_analysis_prompt(model_data)
            
            # Call OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert BIM analyst. Analyze the provided building data and provide insights on complexity, quality, sustainability, and cost efficiency."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis_text": analysis_text,
                "complexity_score": self._extract_score(analysis_text, "complexity"),
                "quality_score": self._extract_score(analysis_text, "quality"),
                "sustainability_score": self._extract_score(analysis_text, "sustainability"),
                "cost_efficiency_score": self._extract_score(analysis_text, "cost_efficiency"),
                "detected_issues": self._extract_issues(analysis_text),
                "recommendations": self._extract_recommendations(analysis_text)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_analysis": self._fallback_analysis(model_data)
            }
    
    def _create_analysis_prompt(self, model_data: Dict[str, Any]) -> str:
        """Create analysis prompt for AI"""
        return f"""
        Analyze this BIM model:
        
        File Name: {model_data.get('file_name', 'Unknown')}
        Schema Version: {model_data.get('schema_version', 'Unknown')}
        Element Count: {model_data.get('element_count', 0)}
        Building Name: {model_data.get('building_name', 'Unknown')}
        Site Name: {model_data.get('site_name', 'Unknown')}
        
        Please provide:
        1. Complexity Score (0-100): How complex is this building model?
        2. Quality Score (0-100): How well-designed is the BIM model?
        3. Sustainability Score (0-100): How sustainable is the design?
        4. Cost Efficiency Score (0-100): How cost-efficient is the design?
        5. Detected Issues: List any potential problems
        6. Recommendations: Suggest improvements
        
        Format your response with clear sections for each score and list.
        """
    
    def _extract_score(self, text: str, score_type: str) -> float:
        """Extract numerical score from AI response"""
        try:
            # Simple extraction logic - in production this would be more sophisticated
            import re
            pattern = rf"{score_type}.*?(\d+)"
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1))
            return 75.0  # Default score
        except:
            return 75.0
    
    def _extract_issues(self, text: str) -> list:
        """Extract detected issues from AI response"""
        try:
            # Simple extraction - look for bullet points or numbered lists
            import re
            issues_section = re.search(r"detected issues:.*?(?=recommendations:|$)", text.lower(), re.DOTALL)
            if issues_section:
                issues_text = issues_section.group(0)
                issues = re.findall(r"[-•*]\s*(.+)", issues_text)
                return issues[:5]  # Limit to 5 issues
            return []
        except:
            return []
    
    def _extract_recommendations(self, text: str) -> list:
        """Extract recommendations from AI response"""
        try:
            import re
            rec_section = re.search(r"recommendations:.*?$", text.lower(), re.DOTALL)
            if rec_section:
                rec_text = rec_section.group(0)
                recommendations = re.findall(r"[-•*]\s*(.+)", rec_text)
                return recommendations[:5]  # Limit to 5 recommendations
            return []
        except:
            return []
    
    def _fallback_analysis(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide fallback analysis when AI is not available"""
        element_count = model_data.get('element_count', 0)
        
        # Basic heuristic-based analysis
        complexity_score = min(100, max(20, element_count / 100 * 10 + 50))
        quality_score = 75.0  # Default quality
        sustainability_score = 70.0  # Default sustainability
        cost_efficiency_score = 80.0  # Default cost efficiency
        
        return {
            "success": True,
            "analysis_text": f"Heuristic analysis of BIM model with {element_count} elements. This appears to be a {'complex' if element_count > 1000 else 'moderate'} building model.",
            "complexity_score": complexity_score,
            "quality_score": quality_score,
            "sustainability_score": sustainability_score,
            "cost_efficiency_score": cost_efficiency_score,
            "detected_issues": ["Analysis performed without AI - limited insights available"],
            "recommendations": ["Consider enabling AI analysis for detailed insights"]
        }


# Create alias for backward compatibility
OpenAIGateway = AIGateway