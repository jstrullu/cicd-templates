#!/usr/bin/env python3
"""Auto-generate the [Unreleased] section of CHANGELOG.md from git commits.

Reads commits since the latest git tag (or all commits if no tag exists),
classifies them by conventional-commit prefix, and rewrites the
[Unreleased] section of CHANGELOG.md while keeping all previous entries.

Commit prefixes mapping:
  feat / add   -> Added
  fix          -> Fixed
  change / refactor -> Changed
  remove / revert   -> Removed
"""

import subprocess
import re
import sys
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANGELOG = os.path.join(REPO_ROOT, "CHANGELOG.md")

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


def get_latest_tag():
    """Return the most recent git tag, or None."""
    try:
        result = subprocess.run(
            ['git', 'describe', '--tags', '--abbrev=0'],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_commits_since(tag):
    """Return list of commit subject lines since the given tag."""
    if tag:
        rev_range = f'{tag}..HEAD'
    else:
        rev_range = 'HEAD'
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
        # Strip conventional-commit scope like "feat(scope): ..."
        clean = re.sub(r'^[a-zA-Z]+(\([^)]*\))?:\s*', '', msg)
        # Try to match a prefix from the original message
        lower_msg = msg.lower()
        category = 'Changed'  # default
        for pattern, cat in CATEGORY_MAP.items():
            if re.match(pattern, lower_msg):
                category = cat
                break
        categorized.setdefault(category, []).append(clean)
    return categorized


def build_unreleased_section(categorized):
    """Build the markdown for the [Unreleased] section."""
    section_order = ['Added', 'Changed', 'Fixed', 'Removed', 'Documentation']
    lines = ["## [Unreleased]", ""]
    for section in section_order:
        if section in categorized:
            lines.append(f"### {section}")
            for entry in categorized[section]:
                lines.append(f"- {entry}")
            lines.append("")
    return "\n".join(lines)


def update_changelog(new_unreleased):
    """Replace the [Unreleased] section in CHANGELOG.md."""
    if not os.path.exists(CHANGELOG):
        print(f"CHANGELOG.md not found at {CHANGELOG}")
        sys.exit(1)

    with open(CHANGELOG, 'r') as f:
        content = f.read()

    # Match from "## [Unreleased]" up to the next "## [" section (or end)
    pattern = r'## \[Unreleased\].*?(?=\n## \[|$)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.start()] + new_unreleased + "\n" + content[match.end():]
    else:
        # No Unreleased section — insert after the header block
        header_end = content.find('\n\n') + 2
        content = content[:header_end] + new_unreleased + "\n\n" + content[header_end:]

    with open(CHANGELOG, 'w') as f:
        f.write(content)

    print("CHANGELOG.md updated successfully.")


def main():
    tag = get_latest_tag()
    print(f"Latest tag: {tag or '(none — using all commits)'}")

    commits = get_commits_since(tag)
    if not commits:
        print("No new commits found. CHANGELOG unchanged.")
        sys.exit(0)

    print(f"Found {len(commits)} commit(s) since {tag or 'beginning'}.")

    categorized = classify_commits(commits)
    unreleased = build_unreleased_section(categorized)
    update_changelog(unreleased)


if __name__ == '__main__':
    main()
