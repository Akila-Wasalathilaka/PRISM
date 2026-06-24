"""
PRISM Analyses API.
Serves PR analysis data to the frontend dashboard.
"""

from typing import Any

from fastapi import APIRouter

from prism.api.webhooks import recent_analyses

router = APIRouter()


@router.get("/")
async def list_analyses(limit: int = 20) -> list[dict[str, Any]]:
    """Return the most recent PR analyses."""
    return recent_analyses[:limit]


@router.get("/stats")
async def get_stats() -> dict[str, Any]:
    """Return aggregate statistics for the dashboard."""
    from collections import Counter

    total = len(recent_analyses)
    if total == 0:
        return {
            "total_analyzed": 0,
            "avg_score": 0,
            "high_risk_count": 0,
            "critical_risk_count": 0,
            "recent_repos": [],
            "total_files_analyzed": 0,
            "total_lines_added": 0,
            "total_lines_deleted": 0,
            "auto_merged_count": 0,
            "top_categories": [],
        }

    scores = [a["score"] for a in recent_analyses]
    avg_score = round(sum(scores) / total, 1)
    high_risk = sum(1 for s in scores if s >= 50)
    critical_risk = sum(1 for s in scores if s >= 70)
    auto_merged_count = sum(1 for s in scores if s == 0)

    total_files = sum(a.get("files_changed", 0) for a in recent_analyses)
    total_added = sum(a.get("additions", 0) for a in recent_analyses)
    total_deleted = sum(a.get("deletions", 0) for a in recent_analyses)

    # Calculate top categories
    category_counter = Counter()
    for a in recent_analyses:
        for cat in a.get("categories", []):
            category_counter[cat] += 1

    top_categories = [{"name": k, "count": v} for k, v in category_counter.most_common(5)]

    # Unique repos from recent analyses
    repos = list({a["repo"] for a in recent_analyses})

    return {
        "total_analyzed": total,
        "avg_score": avg_score,
        "high_risk_count": high_risk,
        "critical_risk_count": critical_risk,
        "recent_repos": repos[:10],
        "total_files_analyzed": total_files,
        "total_lines_added": total_added,
        "total_lines_deleted": total_deleted,
        "auto_merged_count": auto_merged_count,
        "top_categories": top_categories,
    }
