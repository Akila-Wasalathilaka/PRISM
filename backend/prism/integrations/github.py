"""
GitHub App Integration.
Handles JWT authentication and API requests.
"""

import time
from pathlib import Path

import httpx
from jose import jwt

from prism.config import settings


def get_github_jwt() -> str:
    """Generate a JWT for the GitHub App."""
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + (10 * 60), "iss": settings.GITHUB_APP_ID}

    private_key = settings.GITHUB_APP_PRIVATE_KEY
    if private_key.endswith(".pem"):
        path = Path(private_key)
        if not path.is_absolute():
            # Assume it's relative to project root (above backend)
            path = Path(__file__).parent.parent.parent.parent / private_key
        with open(path) as f:
            private_key = f.read()

    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    return encoded_jwt


async def get_installation_token(install_id: int) -> str:
    """Exchange the JWT for an installation access token."""
    jwt_token = get_github_jwt()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.github.com/app/installations/{install_id}/access_tokens",
            headers={
                "Authorization": f"Bearer {jwt_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "PRISM-Bot",
            },
        )
        response.raise_for_status()
        data = response.json()
        return data["token"]


async def get_pull_request_diff(repo_full_name: str, pr_number: int, install_id: int) -> str:
    """Download the raw diff of a pull request."""
    token = await get_installation_token(install_id)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}",
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3.diff",
                "User-Agent": "PRISM-Bot",
            },
        )
        response.raise_for_status()
        return response.text
