"""
PRISM File Classifier.
Maps changed files to risk categories.
"""

import re

CATEGORY_RULES = {
    "database": [r"^migrations/.*\.sql$", r".*models/.*\.py$"],
    "auth": [r".*auth.*\.py$", r".*login.*\.tsx$"],
    "infrastructure": [r".*docker-compose.*", r"^k8s/.*", r".*\.tf$"],
}


class FileClassifier:
    @staticmethod
    def classify_file(filename: str) -> list[str]:
        """Classify a single file path into risk categories."""
        categories = set()
        for category, patterns in CATEGORY_RULES.items():
            for pattern in patterns:
                if re.match(pattern, filename, re.IGNORECASE):
                    categories.add(category)
        return list(categories)
