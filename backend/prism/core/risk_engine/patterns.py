"""
PRISM Risk Patterns.
Deterministic risk detection rules across multiple categories.
"""

import re
from dataclasses import dataclass


@dataclass
class RiskMatch:
    """A single detected risk pattern match."""

    severity: str  # "critical", "high", "medium", "low"
    category: str  # "security", "database", "infrastructure", "code_quality"
    message: str
    filename: str = ""
    line_number: int = 0
    line_content: str = ""


# ── Pattern Definitions ──
# Each pattern: (compiled_regex, severity, category, description)
_PATTERNS: list[tuple[re.Pattern[str], str, str, str]] = [
    # ── Security: Critical ──
    (
        re.compile(r"""(?:password|passwd|pwd)\s*[=:]\s*['"][^'"]+['"]""", re.IGNORECASE),
        "critical",
        "security",
        "Hardcoded password detected",
    ),
    (
        re.compile(
            r"""(?:api_key|apikey|secret_key|access_token|auth_token)\s*[=:]\s*['"][^'"]+['"]""",
            re.IGNORECASE,
        ),
        "critical",
        "security",
        "Hardcoded API key or token detected",
    ),
    (
        re.compile(r"""(?:AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}"""),
        "critical",
        "security",
        "AWS access key detected",
    ),
    (
        re.compile(r"""-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----"""),
        "critical",
        "security",
        "Private key committed to source code",
    ),
    (
        re.compile(r"""(?:eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*)"""),
        "critical",
        "security",
        "Possible JWT token committed to source code",
    ),
    # ── Security: High ──
    (
        re.compile(r"""<script\b[^>]*>[\s\S]*?</script>""", re.IGNORECASE),
        "high",
        "security",
        "Inline script tag detected — potential XSS vector",
    ),
    (
        re.compile(r"""(?:SELECT|INSERT|UPDATE|DELETE)\s+.*\s+(?:WHERE|SET)\s+.*=\s*['"]?\s*\+\s*[a-zA-Z0-9_]+""", re.IGNORECASE),
        "high",
        "security",
        "String concatenation in SQL query — potential SQL injection",
    ),
    (
        re.compile(r"""\beval\s*\("""),
        "high",
        "security",
        "Use of eval() — potential code injection",
    ),
    (
        re.compile(r"""\bexec\s*\("""),
        "high",
        "security",
        "Use of exec() — potential code injection",
    ),
    (
        re.compile(r"""dangerouslySetInnerHTML"""),
        "high",
        "security",
        "dangerouslySetInnerHTML — potential XSS vulnerability",
    ),
    (
        re.compile(r"""verify\s*=\s*False""", re.IGNORECASE),
        "high",
        "security",
        "SSL verification disabled",
    ),
    (
        re.compile(r"""subprocess\.(?:call|run|Popen)\s*\(.*shell\s*=\s*True""", re.DOTALL),
        "high",
        "security",
        "Shell injection risk — subprocess with shell=True",
    ),
    # ── Database: Critical ──
    (
        re.compile(r"""\bDROP\s+TABLE\b""", re.IGNORECASE),
        "critical",
        "database",
        "DROP TABLE detected — destructive migration",
    ),
    (
        re.compile(r"""\bDROP\s+DATABASE\b""", re.IGNORECASE),
        "critical",
        "database",
        "DROP DATABASE detected — catastrophic operation",
    ),
    (
        re.compile(r"""\bTRUNCATE\s+TABLE\b""", re.IGNORECASE),
        "critical",
        "database",
        "TRUNCATE TABLE — all data will be deleted",
    ),
    # ── Database: High ──
    (
        re.compile(r"""\bDELETE\s+FROM\s+\w+\s*(?:;|$)""", re.IGNORECASE),
        "high",
        "database",
        "DELETE FROM without WHERE clause — deletes all rows",
    ),
    (
        re.compile(r"""\bALTER\s+TABLE\b""", re.IGNORECASE),
        "medium",
        "database",
        "ALTER TABLE — schema migration detected",
    ),
    # ── Infrastructure: High ──
    (
        re.compile(r"""chmod\s+777"""),
        "high",
        "infrastructure",
        "Insecure file permissions (chmod 777)",
    ),
    (
        re.compile(r"""USER\s+root""", re.IGNORECASE),
        "high",
        "infrastructure",
        "Dockerfile running as root user",
    ),
    (
        re.compile(r"""0\.0\.0\.0"""),
        "medium",
        "infrastructure",
        "Binding to 0.0.0.0 — exposed to all network interfaces",
    ),
    # ── Code Quality: Medium ──
    (
        re.compile(r"""(?:TODO|FIXME|HACK|XXX)\b"""),
        "low",
        "code_quality",
        "TODO/FIXME marker left in code",
    ),
]


class PatternDetector:
    """Scans diff content for known dangerous patterns."""

    @staticmethod
    def detect_risks(diff: str) -> list[RiskMatch]:
        """Scan raw diff text for known dangerous patterns.

        Args:
            diff: Raw diff text.

        Returns:
            List of RiskMatch objects.
        """
        risks: list[RiskMatch] = []
        for pattern, severity, category, message in _PATTERNS:
            if pattern.search(diff):
                risks.append(RiskMatch(severity=severity, category=category, message=message))
        return risks

    @staticmethod
    def detect_risks_per_file(
        filename: str, added_lines: list[str], line_numbers: list[int]
    ) -> list[RiskMatch]:
        """Scan added lines of a specific file for risk patterns.

        Returns matches with file and line number context for annotations.
        """
        risks: list[RiskMatch] = []
        for i, line in enumerate(added_lines):
            for pattern, severity, category, message in _PATTERNS:
                if pattern.search(line):
                    line_num = line_numbers[i] if i < len(line_numbers) else 0
                    risks.append(
                        RiskMatch(
                            severity=severity,
                            category=category,
                            message=message,
                            filename=filename,
                            line_number=line_num,
                            line_content=line.strip()[:120],
                        )
                    )
        return risks
