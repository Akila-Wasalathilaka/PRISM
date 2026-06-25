"""
GitHub Check Runs Integration.
Posts rich, annotated check runs to pull requests.
"""

import httpx

from prism.core.risk_engine.patterns import RiskMatch
from prism.integrations.github import get_installation_token


def _severity_badge(score: int) -> str:
    """Return an emoji badge based on the risk score."""
    if score >= 70:
        return "🔥 Critical"
    if score >= 50:
        return "🔴 High"
    if score >= 30:
        return "🟡 Medium"
    return "🟢 Low"


def _build_summary(score_data: dict, risks: list[RiskMatch]) -> str:
    """Build a rich markdown summary for the check run output."""
    score = score_data["score"]
    badge = _severity_badge(score)
    breakdown = score_data.get("breakdown", {})
    categories = score_data.get("categories", [])

    lines = [
        f"## {badge} — Risk Score: {score}/100",
        "",
        f"**{score_data.get('total_files', 0)}** files changed "
        f"(**+{score_data.get('total_additions', 0)}** / "
        f"**-{score_data.get('total_deletions', 0)}**)",
        "",
    ]

    # Score breakdown table
    if breakdown:
        lines.append("### Score Breakdown")
        lines.append("")
        lines.append("| Factor | Points |")
        lines.append("|---|---|")
        factor_labels = {
            "categories": "File Categories",
            "patterns": "Risk Patterns",
            "size_penalty": "Diff Size Penalty",
            "file_count_penalty": "File Count Penalty",
        }
        for key, value in breakdown.items():
            label = factor_labels.get(key, key)
            lines.append(f"| {label} | +{value} |")
        lines.append(f"| **Total** | **{score}/100** |")
        lines.append("")

    # Categories hit
    if categories:
        lines.append(f"### Categories: {', '.join(f'`{c}`' for c in categories)}")
        lines.append("")

    # Detected risks
    if risks:
        lines.append("### Detected Risks")
        lines.append("")
        # Deduplicate by message for the summary
        seen: set[str] = set()
        severity_icon = {
            "critical": "🔥",
            "high": "🔴",
            "medium": "🟡",
            "low": "⚪",
        }
        for risk in risks:
            key = f"{risk.message}:{risk.filename}"
            if key in seen:
                continue
            seen.add(key)
            icon = severity_icon.get(risk.severity, "⚪")
            loc = f" (`{risk.filename}` L{risk.line_number})" if risk.filename else ""
            lines.append(f"- {icon} **{risk.severity.upper()}**: {risk.message}{loc}")
        lines.append("")

    return "\n".join(lines)


def _build_annotations(risks: list[RiskMatch]) -> list[dict]:
    """Build GitHub Check Run annotations from risk matches."""
    annotations = []
    seen: set[str] = set()

    for risk in risks:
        if not risk.filename or risk.line_number == 0:
            continue
        # Deduplicate — same file + line + message
        key = f"{risk.filename}:{risk.line_number}:{risk.message}"
        if key in seen:
            continue
        seen.add(key)

        level_map = {"critical": "failure", "high": "failure", "medium": "warning", "low": "notice"}
        annotations.append(
            {
                "path": risk.filename,
                "start_line": risk.line_number,
                "end_line": risk.line_number,
                "annotation_level": level_map.get(risk.severity, "notice"),
                "message": risk.message,
                "title": f"PRISM: {risk.severity.upper()} risk",
            }
        )

    # GitHub limits to 50 annotations per request
    return annotations[:50]


class GitHubCheckRunAPI:
    def __init__(self, install_id: int):
        self.install_id = install_id

    async def create_check_run(
        self,
        repo_full_name: str,
        head_sha: str,
        score_data: dict,
        risks: list[RiskMatch] | None = None,
    ):
        """Create a PRISM check run on a GitHub pull request.

        Args:
            repo_full_name: e.g. "Akila-Wasalathilaka/PRISM"
            head_sha: The commit SHA to attach the check to.
            score_data: Dict from RiskScorer.score_from_diff().
            risks: Optional list of RiskMatch objects for annotations.
        """
        if risks is None:
            risks = []

        score = score_data["score"] if isinstance(score_data, dict) else score_data
        conclusion = "success" if score < 50 else ("action_required" if score < 70 else "failure")

        summary_text = (
            _build_summary(score_data, risks)
            if isinstance(score_data, dict)
            else f"Risk Score: {score}/100"
        )
        annotations = _build_annotations(risks)

        token = await get_installation_token(self.install_id)

        output = {
            "title": f"Risk Score: {score}/100 — {_severity_badge(score)}",
            "summary": summary_text,
        }
        if annotations:
            output["annotations"] = annotations

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{repo_full_name}/check-runs",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "PRISM-Bot",
                },
                json={
                    "name": "PRISM Risk Analysis",
                    "head_sha": head_sha,
                    "status": "completed",
                    "conclusion": conclusion,
                    "output": output,
                },
            )
            response.raise_for_status()
            return response.json()
