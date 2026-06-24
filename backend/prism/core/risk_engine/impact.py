"""
Impact Analysis Module.
Calculates the 'blast radius' and overall structural impact of a Pull Request.
"""

from typing import Any

from prism.core.risk_engine.diff_parser import ParsedDiff
from prism.core.risk_engine.patterns import RiskMatch


class ImpactAnalyzer:
    @staticmethod
    def analyze_impact(parsed_diff: ParsedDiff, risks: list[RiskMatch]) -> dict[str, Any]:
        """
        Analyze the full structural impact of a PR diff.
        Returns a dictionary with blast radius, component changes, and impact tags.
        """
        files_changed = len(parsed_diff.files)
        additions = sum(f.additions for f in parsed_diff.files)
        deletions = sum(f.deletions for f in parsed_diff.files)

        # 1. Determine affected layers
        affected_layers = set()
        has_dependencies = False
        has_database = False
        has_core = False

        for f in parsed_diff.files:
            name = f.filename.lower()
            if "package.json" in name or "requirements.txt" in name or "pipfile" in name:
                has_dependencies = True
                affected_layers.add("Dependencies")
            elif "model" in name or "db" in name or "migration" in name or "sql" in name:
                has_database = True
                affected_layers.add("Database/Schema")
            elif "core" in name or "config" in name or "main" in name or "security" in name:
                has_core = True
                affected_layers.add("Core/Configuration")
            elif "api" in name or "route" in name or "controller" in name:
                affected_layers.add("API/Routing")
            elif (
                "frontend" in name
                or "ui" in name
                or "component" in name
                or ".tsx" in name
                or ".jsx" in name
            ):
                affected_layers.add("Frontend/UI")

        if not affected_layers:
            affected_layers.add("Miscellaneous")

        # 2. Check security impact from risk rules
        has_security_impact = any(
            r.severity in ("critical", "high")
            for r in risks
            if "security" in r.message.lower() or "secret" in r.message.lower()
        )
        if has_security_impact:
            affected_layers.add("Security")

        # 3. Calculate Blast Radius
        # High: changes to DB, Core, Dependencies, or >20 files
        # Medium: >5 files, or API changes
        # Low: isolated UI changes, docs, <5 files
        blast_radius = "Low"
        if (
            has_database
            or has_core
            or has_dependencies
            or files_changed > 20
            or has_security_impact
        ):
            blast_radius = "High"
        elif "API/Routing" in affected_layers or files_changed > 5:
            blast_radius = "Medium"

        return {
            "blast_radius": blast_radius,
            "affected_layers": list(affected_layers),
            "files_changed": files_changed,
            "additions": additions,
            "deletions": deletions,
            "has_security_impact": has_security_impact,
            "has_dependency_impact": has_dependencies,
            "has_database_impact": has_database,
        }
