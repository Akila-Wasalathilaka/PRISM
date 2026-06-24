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

        prompt = f"""You are PRISM, an elite automated security and code review bot.
Analyze the following git diff. Identify any security risks, logic bugs, or bad practices.
Return ONLY a valid JSON array of objects, with NO markdown formatting, NO backticks.
If no risks are found, return an empty array [].

Array format:
[
  {{
    "file": "filename (if known, or 'Global')",
    "line": 0 (approximate line number if known, else 0),
    "message": "A detailed explanation of EXACTLY what the issue is and how to fix it.",
    "severity": "critical" | "high" | "medium" | "low"
  }}
]

Here is the diff:
{diff_text[:15000]}
"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    url,
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {api_key}"
                    },
                    json={
                        "model": "mistral-small-latest",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.1
                    },
                )
                response.raise_for_status()
                data = response.json()

                # Parse the response text as JSON
                text_response = data["choices"][0]["message"]["content"]
                # Clean up any potential markdown formatting the AI might sneak in
                import re
                match = re.search(r'\[.*\]', text_response, re.DOTALL)
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
