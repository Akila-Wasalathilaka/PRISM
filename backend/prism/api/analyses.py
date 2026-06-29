"""
PRISM Analyses API.
Serves PR analysis data and rich statistics to the frontend dashboard.
"""

from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Request

from prism.api.webhooks import recent_analyses
from prism.core.rate_limiter import limiter
from prism.core.risk_engine.llm_provider import get_provider_name

router = APIRouter()


@router.get("")
@router.get("/")
@limiter.limit("60/minute")
async def list_analyses(request: Request, limit: int = 20) -> list[dict[str, Any]]:
    """Return the most recent PR analyses."""
    return recent_analyses[:limit]


@router.get("/stats")
@limiter.limit("60/minute")
async def get_stats(request: Request) -> dict[str, Any]:
    """Return aggregate statistics for the dashboard."""
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
            "safe_pr_percentage": 0,
            "top_categories": [],
            "top_authors": [],
            "risk_trend": [],
            "llm_provider": get_provider_name(),
        }

    scores = [a["score"] for a in recent_analyses]
    avg_score = round(sum(scores) / total, 1)
    high_risk = sum(1 for s in scores if s >= 50)
    critical_risk = sum(1 for s in scores if s >= 70)
    auto_merged_count = sum(1 for a in recent_analyses if a.get("merged", a.get("score") == 0))
    safe_count = sum(1 for s in scores if s == 0)
    safe_pr_percentage = round((safe_count / total) * 100, 1) if total > 0 else 0

    total_files = sum(a.get("files_changed", 0) for a in recent_analyses)
    total_added = sum(a.get("additions", 0) for a in recent_analyses)
    total_deleted = sum(a.get("deletions", 0) for a in recent_analyses)

    # Top risk categories
    category_counter: Counter[str] = Counter()
    for a in recent_analyses:
        for cat in a.get("categories", []):
            category_counter[cat] += 1
    top_categories = [{"name": k, "count": v} for k, v in category_counter.most_common(5)]

    # Top authors by PR count
    author_counter: Counter[str] = Counter()
    for a in recent_analyses:
        author = a.get("author", "unknown")
        author_counter[author] += 1
    top_authors = [{"name": k, "count": v} for k, v in author_counter.most_common(3)]

    # Unique repos
    repos = list({a["repo"] for a in recent_analyses})

    # 7-day risk trend
    risk_trend = _calculate_risk_trend()

    # Project-wise Stats
    project_stats = []
    repo_groups = {}
    for a in recent_analyses:
        repo = a["repo"]
        if repo not in repo_groups:
            repo_groups[repo] = []
        repo_groups[repo].append(a)

    for repo, analyses in repo_groups.items():
        repo_scores = [a["score"] for a in analyses]
        repo_avg = round(sum(repo_scores) / len(repo_scores), 1) if repo_scores else 0
        repo_safe = sum(1 for s in repo_scores if s == 0)
        repo_merged = sum(1 for a in analyses if a.get("merged", a.get("score") == 0))
        repo_critical = sum(1 for s in repo_scores if s >= 70)

        project_stats.append({
            "repo": repo,
            "pr_count": len(analyses),
            "avg_score": repo_avg,
            "safe_prs": repo_safe,
            "auto_merged": repo_merged,
            "critical_risks": repo_critical
        })

    # Sort by PR count descending
    project_stats.sort(key=lambda x: x["pr_count"], reverse=True)

    return {
        "total_analyzed": total,
        "avg_score": avg_score,
        "high_risk_count": high_risk,
        "critical_risk_count": critical_risk,
        "recent_repos": repos[:10],
        "project_stats": project_stats,
        "total_files_analyzed": total_files,
        "total_lines_added": total_added,
        "total_lines_deleted": total_deleted,
        "auto_merged_count": auto_merged_count,
        "safe_pr_percentage": safe_pr_percentage,
        "top_categories": top_categories,
        "top_authors": top_authors,
        "risk_trend": risk_trend,
        "llm_provider": get_provider_name(),
    }


def _calculate_risk_trend() -> list[dict[str, Any]]:
    """Calculate daily average risk scores for the last 7 days."""
    now = datetime.now(UTC)
    trend = []

    for days_ago in range(6, -1, -1):
        day = now - timedelta(days=days_ago)
        day_str = day.strftime("%Y-%m-%d")
        day_label = day.strftime("%a")  # Mon, Tue, etc.

        day_scores = []
        for a in recent_analyses:
            ts = a.get("timestamp", "")
            if ts.startswith(day_str):
                day_scores.append(a["score"])

        trend.append(
            {
                "day": day_label,
                "date": day_str,
                "avg_score": round(sum(day_scores) / len(day_scores), 1) if day_scores else 0,
                "count": len(day_scores),
            }
        )

    return trend
