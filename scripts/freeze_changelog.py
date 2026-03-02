#!/usr/bin/env python3
"""Freeze the [Unreleased] section of CHANGELOG.md for a release.

Accepts a git tag name (e.g. 'v1.2.3' or 'master-1.2.3'), extracts the
version number, then:
  1. Writes the [Unreleased] content to /tmp/release_notes.md
  2. Renames [Unreleased] -> [X.Y.Z] - YYYY-MM-DD
  3. Inserts a fresh empty [Unreleased] section above it
"""

import re
import sys
import os
from datetime import date

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(REPO_ROOT, "CHANGELOG.md")
RELEASE_NOTES_PATH = "/tmp/release_notes.md"


def extract_version(tag):
    """Extract a semver version from a tag like 'v1.2.3' or 'master-1.2.3'."""
    match = re.search(r'(\d+\.\d+\.\d+)', tag)
    if not match:
        print(f"Error: cannot extract version from tag '{tag}'")
        sys.exit(1)
    return match.group(1)


def freeze_changelog(version):
    """Freeze the [Unreleased] section and return the release notes content."""
    if not os.path.exists(CHANGELOG):
        print(f"CHANGELOG.md not found at {CHANGELOG}")
        sys.exit(1)

    with open(CHANGELOG, 'r') as f:
        content = f.read()

    # Extract [Unreleased] section body (between ## [Unreleased] and next ## [)
    pattern = r'## \[Unreleased\]\n(.*?)(?=\n## \[|$)'
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print("Error: no [Unreleased] section found in CHANGELOG.md")
        sys.exit(1)

    release_notes = match.group(1).strip()
    if not release_notes:
        print("Warning: [Unreleased] section is empty.")
        release_notes = "No changes documented."

    # Write release notes to temp file
    with open(RELEASE_NOTES_PATH, 'w') as f:
        f.write(release_notes + "\n")
    print(f"Release notes written to {RELEASE_NOTES_PATH}")

    # Replace [Unreleased] heading with versioned heading, add new empty [Unreleased]
    today = date.today().isoformat()
    new_sections = f"## [Unreleased]\n\n## [{version}] - {today}"
    content = content.replace("## [Unreleased]", new_sections, 1)

    with open(CHANGELOG, 'w') as f:
        f.write(content)

    print(f"CHANGELOG.md frozen: [Unreleased] -> [{version}] - {today}")
    return version


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <tag-name>")
        sys.exit(1)

    tag = sys.argv[1]
    version = extract_version(tag)
    print(f"Tag: {tag} -> version: {version}")
    freeze_changelog(version)


if __name__ == '__main__':
    main()
