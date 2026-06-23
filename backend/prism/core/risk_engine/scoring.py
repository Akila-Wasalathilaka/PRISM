"""
PRISM Risk Scoring (Week 5).
"""

class RiskScorer:
    @staticmethod
    def calculate_score(categories: list[str], patterns: list[dict]) -> int:
        score = 0
        if "auth" in categories:
            score += 30
        if "database" in categories:
            score += 20
            
        for pattern in patterns:
            if pattern["severity"] == "critical":
                score += 50
            elif pattern["severity"] == "high":
                score += 25
                
        return min(score, 100)
