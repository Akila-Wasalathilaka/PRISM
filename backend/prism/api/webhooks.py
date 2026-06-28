"""
PRISM GitHub Webhooks API.
Receives GitHub App webhook events, verifies signatures, and triggers risk analysis.
"""

import asyncio
import hashlib
import hmac
import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException, Request

from prism.config import settings
from prism.core.rate_limiter import limiter
from prism.core.risk_engine.ai_reviewer import AIReviewer
from prism.core.risk_engine.diff_parser import filter_diff, parse_diff
from prism.core.risk_engine.impact import ImpactAnalyzer
from prism.core.risk_engine.patterns import PatternDetector, RiskMatch
from prism.core.risk_engine.scoring import RiskScorer
from prism.integrations.github import (
    get_pull_request_diff,
    merge_pull_request,
    post_pr_comment,
)
from prism.integrations.github_checks import GitHubCheckRunAPI

logger = structlog.get_logger()
router = APIRouter()

# ── Persistent Storage ──
_data_dir = Path(os.environ.get("PRISM_DATA_DIR", "."))
DB_FILE = _data_dir / "dashboard_db.json"

# ── Analysis Cache (repo:pr:sha → result) ──
_analysis_cache: dict[str, dict[str, Any]] = {}
MAX_CACHE_SIZE = 200


def load_analyses() -> list[dict[str, Any]]:
    if DB_FILE.exists():
        try:
            with open(DB_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("dashboard_db.load_error", error=str(e))
    return []


def save_analyses(analyses: list[dict[str, Any]]) -> None:
    try:
        _data_dir.mkdir(parents=True, exist_ok=True)
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(analyses, f, indent=2)
    except Exception as e:
        logger.error("dashboard_db.save_error", error=str(e))


# Persistent store for dashboard
recent_analyses: list[dict[str, Any]] = load_analyses()

# ── Payload size limit (1 MB) ──
MAX_PAYLOAD_SIZE = 1_048_576


def _verify_signature(payload_body: bytes, signature_header: str | None) -> bool:
    """Verify the webhook payload using HMAC-SHA256."""
    secret = settings.GITHUB_WEBHOOK_SECRET
    if not secret:
        # No secret configured — skip verification (dev mode only)
        if settings.ENVIRONMENT == "production":
            logger.warning("webhook.no_secret_in_production")
            return False
        return True

    if not signature_header:
        return False

    expected_sig = (
        "sha256=" + hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
    )

    return hmac.compare_digest(expected_sig, signature_header)


def _generate_impact_report(
    score_data: dict, impact_data: dict, merged: bool, all_risks: list[RiskMatch]
) -> str:
    """Generate a beautifully formatted PR comment for the Impact Report."""
    score = score_data["score"]
    badge = (
        "🟢 Safe"
        if score < 30
        else (
            "🟡 Medium Risk"
            if score < 50
            else ("🔴 High Risk" if score < 70 else "🔥 Critical Risk")
        )
    )

    lines = [
        "## PRISM Codebase Impact Report",
        f"**Risk Score:** `{score}/100` ({badge})",
        "",
        "### 💥 Blast Radius Assessment",
        f"**Estimated Impact:** `{impact_data['blast_radius']}`",
        "",
        f"- **Affected System Layers:** {', '.join(f'`{layer}`' for layer in impact_data['affected_layers'])}",
        f"- **Code Churn:** {impact_data['files_changed']} files (+{impact_data['additions']} / -{impact_data['deletions']})",
    ]

    if impact_data["has_security_impact"]:
        lines.append("- ⚠️ **Security Changes Detected!**")
    if impact_data["has_dependency_impact"]:
        lines.append("- 📦 **Dependency Changes Detected!**")
    if impact_data["has_database_impact"]:
        lines.append("- 🗄️ **Database Schema/Model Changes Detected!**")

    if all_risks:
        lines.append("")
        lines.append("### 🚨 Detected Issues")
        seen: set[str] = set()
        severity_icon = {"critical": "🔥", "high": "🔴", "medium": "🟡", "low": "⚪"}
        for risk in all_risks:
            key = f"{risk.message}:{risk.filename}"
            if key in seen:
                continue
            seen.add(key)
            icon = severity_icon.get(risk.severity, "⚪")
            loc = (
                f" (`{risk.filename}` L{risk.line_number})"
                if getattr(risk, "filename", None)
                else ""
            )
            lines.append(f"- {icon} **{risk.severity.upper()}**: {risk.message}{loc}")

    lines.append("")
    lines.append("### 🤖 Bot Action")
    if merged:
        lines.append("✅ **Zero risks detected.** I have automatically merged this pull request!")
    elif score == 0:
        lines.append(
            "✅ No risks detected, but auto-merge is only supported for fully isolated changes."
        )
    else:
        lines.append(
            "⚠️ **Action Required:** PRISM has detected potential issues in this Pull Request. "
            "Please review the detailed list above, or click the **Checks** tab to see exact "
            "line-by-line annotations in the code before merging."
        )

    return "\n".join(lines)


@router.post("/github")
@limiter.limit("30/minute")
async def github_webhook_receiver(request: Request) -> dict[str, Any]:
    """Receive webhook events from GitHub App."""
    # 1. Enforce payload size limit
    body = await request.body()
    if len(body) > MAX_PAYLOAD_SIZE:
        raise HTTPException(status_code=413, detail="Payload too large")

    # 2. Verify webhook signature
    signature = request.headers.get("x-hub-signature-256")
    if not _verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event_type = request.headers.get("x-github-event")

    # 3. Parse payload
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from e

    # 4. Process pull request events
    if event_type == "pull_request" and payload.get("action") in (
        "opened",
        "synchronize",
        "reopened",
    ):
        repo_full_name = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]
        pr_title = payload["pull_request"].get("title", "")
        head_sha = payload["pull_request"]["head"]["sha"]
        install_id = payload["installation"]["id"]
        author = payload["pull_request"]["user"]["login"]

        # ── Cache check: skip if same SHA already analyzed ──
        cache_key = f"{repo_full_name}:{pr_number}:{head_sha}"
        if cache_key in _analysis_cache:
            logger.info("webhook.cache_hit", repo=repo_full_name, pr=pr_number)
            return _analysis_cache[cache_key]

        logger.info(
            "webhook.analyzing",
            repo=repo_full_name,
            pr=pr_number,
            sha=head_sha[:8],
            author=author,
        )

        # 1. Fetch Diff
        diff_text = await get_pull_request_diff(repo_full_name, pr_number, install_id)
        
        # 1.5 Filter out irrelevant files (docs, lockfiles, self-rules)
        filtered_diff_text = filter_diff(diff_text)

        # 2. Parse the diff into structured data
        parsed_diff = parse_diff(filtered_diff_text)

        # 3. Run pattern detection and AI review in PARALLEL
        async def _run_pattern_detection() -> list[RiskMatch]:
            risks = PatternDetector.detect_risks(filtered_diff_text)
            for diff_file in parsed_diff.files:
                file_risks = PatternDetector.detect_risks_per_file(
                    diff_file.filename, diff_file.added_lines, diff_file.added_line_numbers
                )
                risks.extend(file_risks)
            return risks

        async def _run_ai_review() -> list[RiskMatch]:
            return await AIReviewer.analyze_diff(filtered_diff_text)

        pattern_risks, ai_risks = await asyncio.gather(_run_pattern_detection(), _run_ai_review())
        all_risks = pattern_risks + ai_risks

        # 4. Calculate comprehensive score and structural impact
        score_data = RiskScorer.score_from_diff(parsed_diff, all_risks)
        impact_data = ImpactAnalyzer.analyze_impact(parsed_diff, all_risks)

        # 5. Post rich Check Run
        checks_api = GitHubCheckRunAPI(install_id)
        await checks_api.create_check_run(repo_full_name, head_sha, score_data, all_risks)

        # 6. Auto-merge if risk score is 0 and blast radius is low
        merged = False
        # SECURITY: Only auto-merge if the author is a trusted member of the repository
        author_association = payload["pull_request"].get("author_association", "NONE")
        is_trusted = author_association in ("OWNER", "MEMBER", "COLLABORATOR")

        if score_data["score"] == 0 and impact_data["blast_radius"] == "Low" and is_trusted:
            try:
                await merge_pull_request(repo_full_name, pr_number, install_id)
                merged = True
                logger.info("webhook.auto_merged", repo=repo_full_name, pr=pr_number)
            except Exception as e:
                logger.error(
                    "webhook.merge_failed", repo=repo_full_name, pr=pr_number, error=str(e)
                )

        # 7. Post the Impact Report as a PR comment
        report_md = _generate_impact_report(score_data, impact_data, merged, all_risks)
        try:
            await post_pr_comment(repo_full_name, pr_number, install_id, report_md)
        except Exception as e:
            logger.error("webhook.comment_failed", repo=repo_full_name, pr=pr_number, error=str(e))

        # 8. Store analysis for dashboard
        analysis_record = {
            "repo": repo_full_name,
            "pr_number": pr_number,
            "pr_title": pr_title,
            "author": author,
            "score": score_data["score"],
            "merged": merged,
            "breakdown": score_data.get("breakdown", {}),
            "categories": score_data.get("categories", []),
            "risk_count": len(all_risks),
            "files_changed": score_data.get("total_files", 0),
            "additions": score_data.get("total_additions", 0),
            "deletions": score_data.get("total_deletions", 0),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        recent_analyses.insert(0, analysis_record)
        if len(recent_analyses) > 500:
            recent_analyses.pop()
        save_analyses(recent_analyses)

        # Cache the result
        result = {"status": "processed", "score": score_data["score"], "merged": merged}
        _analysis_cache[cache_key] = result
        if len(_analysis_cache) > MAX_CACHE_SIZE:
            # Evict oldest entry
            oldest_key = next(iter(_analysis_cache))
            del _analysis_cache[oldest_key]

        logger.info(
            "webhook.completed",
            repo=repo_full_name,
            pr=pr_number,
            score=score_data["score"],
            merged=merged,
            risks=len(all_risks),
        )

        return result

    return {"status": "accepted", "event": event_type}
