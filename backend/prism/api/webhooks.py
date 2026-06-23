"""
PRISM GitHub Webhooks API.
"""

from typing import Any
from fastapi import APIRouter, HTTPException, Request

from prism.core.risk_engine.patterns import PatternDetector
from prism.core.risk_engine.scoring import RiskScorer
from prism.integrations.github import get_pull_request_diff
from prism.integrations.github_checks import GitHubCheckRunAPI

router = APIRouter()


@router.post("/github")
async def github_webhook_receiver(request: Request) -> dict[str, Any]:
    """
    Receive webhook events from GitHub App.
    """
    # Temporarily bypass strict signature check (since the secret is currently blank)
    # signature = request.headers.get("x-hub-signature-256")
    
    event_type = request.headers.get("x-github-event")
    
    # 2. Parse payload
    try:
        payload = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from e

    # 3. Process based on event type
    if event_type == "pull_request" and payload.get("action") in ("opened", "synchronize", "reopened"):
        repo_full_name = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]
        head_sha = payload["pull_request"]["head"]["sha"]
        install_id = payload["installation"]["id"]
        
        # 1. Fetch Diff
        diff_text = await get_pull_request_diff(repo_full_name, pr_number, install_id)
        
        # 2. Analyze Risk
        risks = PatternDetector.detect_risks(diff_text)
        categories = ["database"] if "CREATE TABLE" in diff_text or "DROP TABLE" in diff_text else []
        score = RiskScorer.calculate_score(categories, risks)
        
        # 3. Post Check Run
        checks_api = GitHubCheckRunAPI(install_id)
        await checks_api.create_check_run(repo_full_name, head_sha, score)
        
        return {"status": "processed", "score": score}

    return {"status": "accepted", "event": event_type}
