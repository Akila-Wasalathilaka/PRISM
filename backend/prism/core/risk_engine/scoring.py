"""
PRISM Risk Scoring.
Weighted scoring formula using file classification, pattern severity, and diff size.
"""

from prism.core.risk_engine.classifier import FileClassifier
from prism.core.risk_engine.diff_parser import ParsedDiff
from prism.core.risk_engine.patterns import RiskMatch

# ── Weight Configuration ──
SEVERITY_WEIGHTS = {
    "critical": 30,
    "high": 15,
    "medium": 8,
    "low": 3,
}

CATEGORY_WEIGHTS = {
    "auth": 15,
    "database": 12,
    "infrastructure": 10,
}

# Diff size thresholds for penalty
SIZE_THRESHOLDS = [
    (1000, 20),  # >1000 changes → +20
    (500, 12),  # >500 changes  → +12
    (200, 5),  # >200 changes  → +5
]


class RiskScorer:
    """Calculates a composite risk score from structured analysis data."""

    @staticmethod
    def calculate_score(categories: list[str], patterns: list[dict]) -> int:
        """Legacy scoring method for backward compatibility."""
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

    @staticmethod
    def score_from_diff(parsed_diff: ParsedDiff, risks: list[RiskMatch]) -> dict:
        """Calculate a comprehensive risk score from parsed diff and detected risks.

        Returns a dict with the total score and a breakdown of contributions.
        """
        breakdown: dict[str, int] = {}

        # ── 1. Category Score ──
        # Classify every changed file and accumulate category weights
        all_categories: set[str] = set()
        for diff_file in parsed_diff.files:
            file_cats = FileClassifier.classify_file(diff_file.filename)
            all_categories.update(file_cats)

        category_score = 0
        for cat in all_categories:
            weight = CATEGORY_WEIGHTS.get(cat, 0)
            category_score += weight
        if category_score:
            breakdown["categories"] = category_score

        # ── 2. Pattern Score ──
        # Deduplicate by message to avoid double-counting the same rule
        seen_messages: set[str] = set()
        pattern_score = 0
        for risk in risks:
            if risk.message not in seen_messages:
                seen_messages.add(risk.message)
                weight = SEVERITY_WEIGHTS.get(risk.severity, 0)
                pattern_score += weight
        if pattern_score:
            breakdown["patterns"] = pattern_score

        # ── 3. Size Penalty ──
        size_score = 0
        total_changes = parsed_diff.total_changes
        for threshold, penalty in SIZE_THRESHOLDS:
            if total_changes > threshold:
                size_score = penalty
                break
        if size_score:
            breakdown["size_penalty"] = size_score

        # ── 4. File Count Penalty ──
        file_count = len(parsed_diff.files)
        file_penalty = 0
        if file_count > 20:
            file_penalty = 10
        elif file_count > 10:
            file_penalty = 5
        if file_penalty:
            breakdown["file_count_penalty"] = file_penalty

        total = category_score + pattern_score + size_score + file_penalty
        total = min(total, 100)

        return {
            "score": total,
            "breakdown": breakdown,
            "categories": sorted(all_categories),
            "total_files": file_count,
            "total_additions": parsed_diff.total_additions,
            "total_deletions": parsed_diff.total_deletions,
        }
