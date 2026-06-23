"""
GitHub Check Runs Integration (Week 7).
"""

import httpx
from prism.integrations.github import get_installation_token

class GitHubCheckRunAPI:
    def __init__(self, install_id: int):
        self.install_id = install_id

    async def create_check_run(self, repo_full_name: str, head_sha: str, score: int):
        """Create a PRISM check run on a GitHub pull request."""
        status = "completed"
        conclusion = "success" if score < 70 else "action_required"
        
        token = await get_installation_token(self.install_id)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.github.com/repos/{repo_full_name}/check-runs",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "PRISM-Bot"
                },
                json={
                    "name": "PRISM Risk Analysis",
                    "head_sha": head_sha,
                    "status": status,
                    "conclusion": conclusion,
                    "output": {
                        "title": f"Risk Score: {score}/100",
                        "summary": "PRISM has analyzed the code changes.",
                        "text": f"This pull request has been assigned a risk score of {score}. If the score exceeds the threshold, manual review is highly recommended."
                    }
                }
            )
            response.raise_for_status()
            return response.json()
