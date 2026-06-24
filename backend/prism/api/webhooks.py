"""
PRISM GitHub Webhooks API.
Receives GitHub App webhook events, verifies signatures, and triggers risk analysis.
"""

import hashlib
import hmac
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from prism.config import settings
from prism.core.risk_engine.diff_parser import parse_diff
from prism.core.risk_engine.patterns import PatternDetector
from prism.core.risk_engine.scoring import RiskScorer
from prism.integrations.github import get_pull_request_diff
from prism.integrations.github_checks import GitHubCheckRunAPI

router = APIRouter()

# In-memory store for recent analyses (used by the dashboard API)
recent_analyses: list[dict[str, Any]] = []


def _verify_signature(payload_body: bytes, signature_header: str | None) -> bool:
    """Verify the webhook payload using HMAC-SHA256.

    If GITHUB_WEBHOOK_SECRET is not configured, verification is skipped
    to allow development without a secret.
    """
    secret = settings.GITHUB_WEBHOOK_SECRET
    if not secret:
        # No secret configured — skip verification (dev mode)
        return True

    if not signature_header:
        return False

    expected_sig = (
        "sha256=" + hmac.new(secret.encode("utf-8"), payload_body, hashlib.sha256).hexdigest()
    )

    return hmac.compare_digest(expected_sig, signature_header)


@router.post("/github")
async def github_webhook_receiver(request: Request) -> dict[str, Any]:
    """
    Receive webhook events from GitHub App.
    """
    # 1. Verify webhook signature
    body = await request.body()
    signature = request.headers.get("x-hub-signature-256")

    if not _verify_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event_type = request.headers.get("x-github-event")

    # 2. Parse payload
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from e

    # 3. Process pull request events
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

        # 1. Fetch Diff
        diff_text = await get_pull_request_diff(repo_full_name, pr_number, install_id)

        # 2. Parse the diff into structured data
        parsed_diff = parse_diff(diff_text)

        # 3. Detect risks — both global and per-file with line numbers
        all_risks = PatternDetector.detect_risks(diff_text)
        for diff_file in parsed_diff.files:
            file_risks = PatternDetector.detect_risks_per_file(
                diff_file.filename, diff_file.added_lines, diff_file.added_line_numbers
            )
            all_risks.extend(file_risks)

        # 4. Calculate comprehensive score
        score_data = RiskScorer.score_from_diff(parsed_diff, all_risks)

        # 5. Post rich Check Run
        checks_api = GitHubCheckRunAPI(install_id)
        await checks_api.create_check_run(repo_full_name, head_sha, score_data, all_risks)

        # 6. Store analysis for dashboard
        analysis_record = {
            "repo": repo_full_name,
            "pr_number": pr_number,
            "pr_title": pr_title,
            "author": author,
            "score": score_data["score"],
            "breakdown": score_data.get("breakdown", {}),
            "categories": score_data.get("categories", []),
            "risk_count": len(all_risks),
            "files_changed": score_data.get("total_files", 0),
            "additions": score_data.get("total_additions", 0),
            "deletions": score_data.get("total_deletions", 0),
            "timestamp": datetime.now(UTC).isoformat(),
        }
        recent_analyses.insert(0, analysis_record)
        # Keep only last 100 analyses in memory
        if len(recent_analyses) > 100:
            recent_analyses.pop()

        return {"status": "processed", "score": score_data["score"]}

    return {"status": "accepted", "event": event_type}
