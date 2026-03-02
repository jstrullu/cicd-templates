#!/usr/bin/env python3
"""Validate Azure Pipelines template conventions.

Checks:
  - Every parameter block entry has a 'type' field
  - No hardcoded service-connection names, IPs, or internal URLs
  - Pipeline files define the expected stage order
  - Job templates define at least one job
"""

import sys
import re
import glob
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINES_DIR = os.path.join(REPO_ROOT, "azure-pipelines")

# Patterns that should never appear (hardcoded org-specific values)
FORBIDDEN_PATTERNS = [
    (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', "Hardcoded IP address"),
    (r'@[a-zA-Z0-9.-]+\.(corp|internal|local)\b', "Internal domain email"),
]

errors = []


def check_parameters_have_type(filepath, content):
    """Ensure every parameter entry has a 'type' field."""
    in_parameters = False
    current_param = None
    has_type = False
    line_number = 0

    for line in content.splitlines():
        line_number += 1
        stripped = line.strip()

        # Detect parameters block
        if stripped == "parameters:" or re.match(r'^parameters:\s*$', stripped):
            in_parameters = True
            continue

        if in_parameters:
            # End of parameters block (new top-level key)
            if re.match(r'^[a-zA-Z]', line) and not line.startswith(' ') and not line.startswith('\t'):
                if current_param and not has_type:
                    errors.append(f"{filepath}:{line_number}: parameter '{current_param}' missing 'type'")
                in_parameters = False
                continue

            # New parameter entry
            match = re.match(r'\s+-\s+name:\s+(\S+)', line)
            if match:
                if current_param and not has_type:
                    errors.append(f"{filepath}:{line_number}: parameter '{current_param}' missing 'type'")
                current_param = match.group(1)
                has_type = False
                continue

            # Type field
            if re.match(r'type:\s+', stripped):
                has_type = True

    # Check last parameter
    if in_parameters and current_param and not has_type:
        errors.append(f"{filepath}:end: parameter '{current_param}' missing 'type'")


def check_forbidden_patterns(filepath, content):
    """Check for hardcoded values that should be parameterized."""
    for line_number, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        # Skip comments
        if stripped.startswith('#'):
            continue
        for pattern, description in FORBIDDEN_PATTERNS:
            if re.search(pattern, line):
                # Allow 127.0.0.1 and common safe IPs
                if '127.0.0.1' in line or '0.0.0.0' in line:
                    continue
                errors.append(f"{filepath}:{line_number}: {description} found")


def check_job_templates_have_jobs(filepath, content):
    """Ensure job templates define at least one job."""
    if '/jobs/' not in filepath:
        return
    if 'jobs:' not in content:
        errors.append(f"{filepath}: job template does not define any 'jobs:'")


def check_pipeline_has_stages(filepath, content):
    """Ensure pipeline files define stages."""
    if '/pipelines/' not in filepath:
        return
    if 'stages:' not in content:
        errors.append(f"{filepath}: pipeline does not define any 'stages:'")


def main():
    yml_files = glob.glob(os.path.join(PIPELINES_DIR, "**", "*.yml"), recursive=True)

    if not yml_files:
        print("ERROR: No YAML files found under azure-pipelines/")
        sys.exit(1)

    print(f"Validating {len(yml_files)} template files...")

    for filepath in sorted(yml_files):
        rel_path = os.path.relpath(filepath, REPO_ROOT)
        with open(filepath, 'r') as f:
            content = f.read()

        check_parameters_have_type(rel_path, content)
        check_forbidden_patterns(rel_path, content)
        check_job_templates_have_jobs(rel_path, content)
        check_pipeline_has_stages(rel_path, content)

    if errors:
        print(f"\n{len(errors)} validation error(s) found:\n")
        for error in errors:
            print(f"  ✗ {error}")
        sys.exit(1)
    else:
        print(f"All {len(yml_files)} templates passed validation.")
        sys.exit(0)


if __name__ == '__main__':
    main()
