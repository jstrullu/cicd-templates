#!/usr/bin/env python3
"""Freeze the [Unreleased] section of CHANGELOG.md for a release.

Accepts a git tag name (e.g. 'v1.2.3' or '0.7.0'), extracts the version
number, then:
  1. Generates release notes from commits between the previous tag and this tag
  2. Writes release notes to /tmp/release_notes.md
  3. Replaces [Unreleased] with [X.Y.Z] - YYYY-MM-DD containing the notes
  4. Inserts a fresh empty [Unreleased] section above it

This script is self-contained: it generates content from git history rather
than relying on the [Unreleased] section being pre-populated.
"""

import subprocess
import re
import sys
import os
from datetime import date

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(REPO_ROOT, "CHANGELOG.md")
RELEASE_NOTES_PATH = "/tmp/release_notes.md"

# Same category map as generate_changelog.py
CATEGORY_MAP = {
    r'^feat': 'Added',
    r'^add': 'Added',
    r'^fix': 'Fixed',
    r'^change': 'Changed',
    r'^update': 'Changed',
    r'^refactor': 'Changed',
    r'^remove': 'Removed',
    r'^revert': 'Removed',
    r'^doc': 'Documentation',
}

# Commits matching these patterns are excluded from the changelog
SKIP_PATTERNS = [
    r'\[skip ci\]',
    r'^chore:',
    r'^Merge pull request',
    r'^Merge branch',
]


def extract_version(tag):
    """Extract a semver version from a tag like 'v1.2.3' or '0.7.0'."""
    match = re.search(r'(\d+\.\d+\.\d+)', tag)
    if not match:
        print(f"Error: cannot extract version from tag '{tag}'")
        sys.exit(1)
    return match.group(1)


def get_previous_tag(current_tag):
    """Return the tag before current_tag, or None if there is no previous tag."""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0', f'{current_tag}^'],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_commits_between(from_ref, to_ref):
    """Return list of commit subject lines between two refs."""
    if from_ref:
        rev_range = f'{from_ref}..{to_ref}'
    else:
        rev_range = to_ref
    result = subprocess.run(
        ['git', 'log', rev_range, '--pretty=format:%s'],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    if result.returncode != 0:
        return []
    commits = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    # Filter out noise (CI commits, merges, chores)
    filtered = []
    for msg in commits:
        if any(re.search(p, msg) for p in SKIP_PATTERNS):
            continue
        filtered.append(msg)
    return filtered


def classify_commits(commits):
    """Classify commits into changelog categories."""
    categorized = {}
    for msg in commits:
        clean = re.sub(r'^[a-zA-Z]+(\([^)]*\))?:\s*', '', msg)
        lower_msg = msg.lower()
        category = 'Changed'
        for pattern, cat in CATEGORY_MAP.items():
            if re.match(pattern, lower_msg):
                category = cat
                break
        categorized.setdefault(category, []).append(clean)
    return categorized


def build_release_notes(categorized):
    """Build markdown content for a release (without the heading)."""
    section_order = ['Added', 'Changed', 'Fixed', 'Removed', 'Documentation']
    lines = []
    for section in section_order:
        if section in categorized:
            lines.append(f"### {section}")
            for entry in categorized[section]:
                lines.append(f"- {entry}")
            lines.append("")
    return "\n".join(lines).strip()


def freeze_changelog(version, current_tag):
    """Generate release notes from git and freeze them into CHANGELOG.md."""
    if not os.path.exists(CHANGELOG):
        print(f"CHANGELOG.md not found at {CHANGELOG}")
        sys.exit(1)

    with open(CHANGELOG, 'r') as f:
        content = f.read()

    # Bail out if this version is already frozen (idempotency / duplicate protection)
    if f'## [{version}]' in content:
        print(f"Version [{version}] already exists in CHANGELOG.md. Skipping freeze.")
        # Still write release notes for the GitHub release
        pattern = rf'## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|$)'
        match = re.search(pattern, content, re.DOTALL)
        notes = match.group(1).strip() if match else "No changes documented."
        with open(RELEASE_NOTES_PATH, 'w') as f:
            f.write(notes + "\n")
        return version

    # Generate content from git history
    prev_tag = get_previous_tag(current_tag)
    print(f"Previous tag: {prev_tag or '(none — using all commits)'}")

    commits = get_commits_between(prev_tag, current_tag)
    if commits:
        categorized = classify_commits(commits)
        release_notes = build_release_notes(categorized)
    else:
        release_notes = "No changes documented."

    print(f"Generated release notes from {len(commits)} commit(s).")

    # Write release notes to temp file for GitHub release
    with open(RELEASE_NOTES_PATH, 'w') as f:
        f.write(release_notes + "\n")
    print(f"Release notes written to {RELEASE_NOTES_PATH}")

    # Replace [Unreleased] section with versioned section
    today = date.today().isoformat()
    version_heading = f"## [{version}] - {today}"
    new_content = f"## [Unreleased]\n\n{version_heading}\n\n{release_notes}\n"

    unreleased_pattern = r'## \[Unreleased\].*?(?=\n## \[|$)'
    match = re.search(unreleased_pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_content + "\n" + content[match.end():]
    else:
        # No Unreleased section — insert after the header block
        header_end = content.find('\n\n') + 2
        content = content[:header_end] + new_content + "\n" + content[header_end:]

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
    freeze_changelog(version, tag)


if __name__ == '__main__':
    main()
