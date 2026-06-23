"""
GitHub Check Runs Integration (Week 7).
"""


class GitHubCheckRunAPI:
    def __init__(self, install_id: int):
        self.install_id = install_id

    async def create_check_run(self, repo_full_name: str, head_sha: str, score: int):
        """Create a PRISM check run on a GitHub pull request."""
        status = "completed"
        conclusion = "success" if score < 70 else "action_required"
        # Simulate API call to GitHub
        return {"status": status, "conclusion": conclusion, "score": score}
