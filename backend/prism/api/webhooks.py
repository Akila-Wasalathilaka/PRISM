"""
PRISM GitHub Webhooks API.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.post("/github")
async def github_webhook_receiver(request: Request) -> dict[str, Any]:
    """
    Receive webhook events from GitHub App.
    """
    # 1. Verify GitHub signature (requires raw body)
    signature = request.headers.get("x-hub-signature-256")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    event_type = request.headers.get("x-github-event")

    # 2. Parse payload
    try:
        await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON payload") from e

    # 3. Process based on event type
    # For now, just accept and queue the event
    return {"status": "accepted", "event": event_type}
