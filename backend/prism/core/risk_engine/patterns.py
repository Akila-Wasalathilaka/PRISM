"""
PRISM Risk Patterns.
Deterministic risk detection rules.
"""

from typing import List, Dict

class PatternDetector:
    @staticmethod
    def detect_risks(diff: str) -> List[Dict[str, str]]:
        """Scan a diff for known dangerous patterns."""
        risks = []
        if "DROP TABLE" in diff.upper():
            risks.append({"severity": "critical", "message": "DROP TABLE detected"})
        if "password=" in diff.lower() or "secret=" in diff.lower():
            risks.append({"severity": "high", "message": "Potential hardcoded secret detected"})
        if "chmod 777" in diff:
            risks.append({"severity": "high", "message": "Insecure file permissions (chmod 777)"})
        return risks
