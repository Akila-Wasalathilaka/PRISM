"""
PRISM Diff Parser.
Parses unified diff format into structured data for analysis.
"""

import re
from dataclasses import dataclass, field


@dataclass
class DiffFile:
    """Represents a single file changed in a diff."""

    filename: str
    added_lines: list[str] = field(default_factory=list)
    removed_lines: list[str] = field(default_factory=list)
    added_line_numbers: list[int] = field(default_factory=list)
    additions: int = 0
    deletions: int = 0


@dataclass
class ParsedDiff:
    """Represents the complete parsed diff of a pull request."""

    files: list[DiffFile] = field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0

    @property
    def total_changes(self) -> int:
        return self.total_additions + self.total_deletions

    @property
    def filenames(self) -> list[str]:
        return [f.filename for f in self.files]


# Regex to match the file header in unified diff format
_DIFF_FILE_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)$", re.MULTILINE)
_HUNK_HEADER_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", re.MULTILINE)


def parse_diff(raw_diff: str) -> ParsedDiff:
    """Parse a raw unified diff string into structured data.

    Args:
        raw_diff: The raw diff text from GitHub API.

    Returns:
        A ParsedDiff object with per-file breakdowns.
    """
    result = ParsedDiff()

    # Split by file boundaries
    file_sections = _DIFF_FILE_RE.split(raw_diff)

    # file_sections[0] is empty or preamble
    # Then groups of 3: (old_path, new_path, content)
    i = 1
    while i + 2 < len(file_sections):
        _old_path = file_sections[i]
        new_path = file_sections[i + 1]
        content = file_sections[i + 2]
        i += 3

        diff_file = DiffFile(filename=new_path)

        # Parse hunks within this file
        hunks = _HUNK_HEADER_RE.split(content)

        # Process each hunk — hunks[0] is before first @@, then alternating
        # (start_line, hunk_content)
        j = 1
        while j + 1 < len(hunks):
            start_line = int(hunks[j])
            hunk_content = hunks[j + 1]
            j += 2

            current_line = start_line
            for line in hunk_content.splitlines():
                if line.startswith("+"):
                    diff_file.added_lines.append(line[1:])
                    diff_file.added_line_numbers.append(current_line)
                    diff_file.additions += 1
                    current_line += 1
                elif line.startswith("-"):
                    diff_file.removed_lines.append(line[1:])
                    diff_file.deletions += 1
                    # Removed lines don't advance the new-file line counter
                else:
                    current_line += 1

        result.files.append(diff_file)
        result.total_additions += diff_file.additions
        result.total_deletions += diff_file.deletions

    return result
