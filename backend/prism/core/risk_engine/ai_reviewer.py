"""
AI Semantic Code Reviewer.
Uses the Mistral API to analyze PR diffs and provide exact, human-readable explanations of risks.
"""

import httpx

from prism.config import settings
from prism.core.risk_engine.patterns import RiskMatch


class AIReviewer:
    @staticmethod
    async def analyze_diff(diff_text: str) -> list[RiskMatch]:
        """
        Analyze a git diff using the Mistral API.
        Returns a list of detailed RiskMatches.
        """
        api_key = settings.MISTRAL_API_KEY
        if not api_key:
            return []

        url = "https://api.mistral.ai/v1/chat/completions"

        prompt = f"""You are PRISM, an expert code reviewer. Analyze this diff for security risks, logic bugs, and bad practices.

Rules:
1. Explain the issue and how to fix it clearly and concisely. Avoid unnecessary preamble, filler words, or overly long explanations to optimize token usage.
2. DO NOT hallucinate or guess the structure of classes/functions not present in the diff (assume imported objects are correct).
3. Return ONLY a valid JSON array. No markdown, no backticks.
4. If no issues, return [].

Format:
[{{
  "file": "filename",
  "line": line_number,
  "message": "Concise issue description and fix.",
  "severity": "critical" | "high" | "medium" | "low"
}}]

Diff:
{diff_text[:15000]}
"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}",
                    },
                    json={
                        "model": "mistral-small-latest",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1,
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Parse the response text as JSON
                text_response = data["choices"][0]["message"]["content"]
                # Clean up any potential markdown formatting the AI might sneak in
                import re

                match = re.search(r"\[.*\]", text_response, re.DOTALL)
                if match:
                    text_response = match.group(0)

                import json

                ai_risks = json.loads(text_response)

                matches = []
                for risk in ai_risks:
                    matches.append(
                        RiskMatch(
                            filename=risk.get("file", "Global"),
                            line_number=risk.get("line", 0),
                            message=f"🤖 **Mistral AI Analysis:** {risk.get('message', 'Risk detected.')}",
                            severity=risk.get("severity", "medium"),
                            category="ai_review",
                        )
                    )
                return matches

            except Exception as e:
                print(f"Mistral AI Review Failed: {e}")
                return []
