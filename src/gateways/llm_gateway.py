from typing import Dict, List
import re


class SimpleLLMGateway:
    def __init__(self):
        self.safety_keywords = [
            "exit",
            "emergency",
            "fire",
            "stairs",
            "ventilation",
            "structural",
            "load-bearing",
            "foundation",
        ]

    async def analyze_bim_file(self, file_content: str) -> Dict:
        """Simple keyword-based analysis of BIM file content"""
        # Convert bytes to string if needed
        if isinstance(file_content, bytes):
            file_content = file_content.decode("utf-8")

        # Count safety-related keywords
        keyword_counts = {
            keyword: len(re.findall(rf"\b{keyword}\b", file_content.lower()))
            for keyword in self.safety_keywords
        }

        # Simple scoring based on keyword presence
        safety_score = sum(keyword_counts.values()) / len(self.safety_keywords)

        return {
            "safety_score": min(safety_score, 1.0),
            "keywords_found": keyword_counts,
            "recommendations": self._generate_recommendations(keyword_counts),
        }

    def _generate_recommendations(self, keyword_counts: Dict[str, int]) -> List[str]:
        """Generate basic recommendations based on keyword analysis"""
        recommendations = []

        if keyword_counts.get("fire", 0) < 1:
            recommendations.append("Add fire safety specifications")
        if keyword_counts.get("exit", 0) < 1:
            recommendations.append("Include emergency exit details")
        if keyword_counts.get("structural", 0) < 1:
            recommendations.append("Add structural integrity information")

        return recommendations or ["No specific recommendations"]


class SimpleLLMGateway:
    async def analyze_bim_file(self, file_content):
        """Mock LLM analysis of BIM file"""
        return {
            "summary": "BIM file analysis (mock)",
            "elements": {"walls": 12, "windows": 8, "doors": 4},
            "estimated_cost": 250000,
        }
