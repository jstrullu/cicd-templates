#!/usr/bin/env python3
"""Static contract validation for CI/CD templates (Azure Pipelines + GitHub Actions).

Complements `validate_templates.py` (which checks conventions on azure-pipelines/ only).
This script checks that templates *fit together*:

  Azure Pipelines (`- template: <path>` with optional `parameters:` block)
    A1. Reference resolves     — the target file exists.
    A2. Unknown parameter      — every passed parameter is declared in the target.
    A3. Missing required param — every target parameter without `default` is passed.

  GitHub Actions (`uses: <ref>` with optional `with:` block)
    G1. Reference resolves     — internal composite action `action.yml` exists.
    G2. Unknown input          — every `with:` key is a declared `inputs:` of the target.
    G3. Missing required input — every `required: true` input without `default` is passed.

Out of scope (documented limitations, not checked here):
    - Azure parameter *type* consistency (bonus).
    - GitHub `steps.<x>.outputs.<y>` traceability (bonus) — fragile under `${{ }}`.
    - External GitHub actions (actions/checkout, docker/*, ...) — not our contract.

Exit code: non-zero if at least one contract violation, zero otherwise.
No pipeline is executed — pure static parsing + reference resolution.
"""

import os
import sys

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

# French messages + Unicode marks: force UTF-8 output (Windows console is cp1252).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AZURE_DIR = os.path.join(REPO_ROOT, "azure-pipelines")
GITHUB_DIR = os.path.join(REPO_ROOT, "github-actions")

# Internal GitHub repo alias. `uses: jstrullu/cicd/<path>@<ref>` maps <path> onto REPO_ROOT.
GITHUB_INTERNAL_PREFIX = "jstrullu/cicd/"

_yaml = YAML(typ="rt")  # round-trip loader keeps line numbers via .lc

errors = []  # list of "file:line : message" strings


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #

def load_yaml(filepath):
    """Parse a YAML file, returning the root node or None on failure."""
    try:
        with open(filepath, "r", encoding="utf-8") as fh:
            return _yaml.load(fh)
    except Exception as exc:  # noqa: BLE001 - report and keep going
        rel = os.path.relpath(filepath, REPO_ROOT)
        errors.append(f"{rel}:1 : fichier YAML illisible ({exc})")
        return None


def key_line(node, key):
    """1-based line of `key` inside a CommentedMap (best effort, 0 if unknown)."""
    try:
        return node.lc.data[key][0] + 1
    except Exception:  # noqa: BLE001
        return 0


def walk(node, visit):
    """Depth-first walk over the YAML tree, calling visit(map) on every mapping."""
    if isinstance(node, CommentedMap):
        visit(node)
        for value in node.values():
            walk(value, visit)
    elif isinstance(node, CommentedSeq):
        for item in node:
            walk(item, visit)


# --------------------------------------------------------------------------- #
# Azure Pipelines
# --------------------------------------------------------------------------- #

def resolve_azure_template(ref, current_file):
    """Resolve an Azure `- template:` value to an absolute path, or None if unresolvable.

    Handles three forms:
      - cross-repo `path@alias`  -> strip the alias, resolve `path` from the repo root
      - absolute `/jobs/...`     -> mapped onto REPO_ROOT *and* azure-pipelines/ (either wins)
      - relative `..\\steps\\x`  -> resolved from the including file's directory
    Returns the first existing candidate, else the primary candidate (for the error message).
    """
    ref = str(ref)

    # Cross-repo reference: keep only the path part before "@alias".
    if "@" in ref:
        ref = ref.split("@", 1)[0]

    # Normalize Windows-style backslashes used in job -> step references.
    ref = ref.replace("\\", "/")

    if ref.startswith("/"):
        rel = ref.lstrip("/")
        # Absolute "/" = repository root. Locally that is either the repo root
        # itself or the azure-pipelines/ sub-root, depending on the template's
        # own convention (both `/jobs/...` and `/azure-pipelines/jobs/...` exist).
        candidates = [
            os.path.join(REPO_ROOT, rel),
            os.path.join(AZURE_DIR, rel),
        ]
    else:
        base = os.path.dirname(current_file)
        candidates = [os.path.normpath(os.path.join(base, ref))]

    for cand in candidates:
        if os.path.isfile(cand):
            return cand
    return candidates[0]


def declared_azure_params(target_path):
    """Return {name: has_default} for the `parameters:` of an Azure template."""
    node = load_yaml(target_path)
    declared = {}
    if not isinstance(node, CommentedMap):
        return declared
    params = node.get("parameters")
    if isinstance(params, CommentedSeq):
        for entry in params:
            if isinstance(entry, CommentedMap) and "name" in entry:
                declared[str(entry["name"])] = "default" in entry
    return declared


def check_azure_file(filepath):
    rel = os.path.relpath(filepath, REPO_ROOT)
    root = load_yaml(filepath)
    if root is None:
        return

    calls = []  # collect every mapping that includes another template

    def visit(node):
        if "template" in node:
            calls.append(node)

    walk(root, visit)

    for call in calls:
        ref = call["template"]
        line = key_line(call, "template")
        target = resolve_azure_template(ref, filepath)

        # A1 — reference resolves.
        if not os.path.isfile(target):
            errors.append(
                f"{rel}:{line} : référence de template introuvable « {ref} »"
            )
            continue

        passed = call.get("parameters")
        passed_names = set()
        if isinstance(passed, CommentedMap):
            passed_names = {str(k) for k in passed.keys()}

        declared = declared_azure_params(target)
        target_rel = os.path.relpath(target, REPO_ROOT)

        # A2 — unknown parameter passed.
        for name in passed_names:
            if name not in declared:
                pline = key_line(passed, name) if isinstance(passed, CommentedMap) else line
                errors.append(
                    f"{rel}:{pline} : paramètre « {name} » passé au template "
                    f"« {target_rel} » mais non déclaré"
                )

        # A3 — required parameter (no default) not passed.
        for name, has_default in declared.items():
            if not has_default and name not in passed_names:
                errors.append(
                    f"{rel}:{line} : paramètre requis « {name} » du template "
                    f"« {target_rel} » non fourni"
                )


# --------------------------------------------------------------------------- #
# GitHub Actions
# --------------------------------------------------------------------------- #

def resolve_github_action(ref):
    """Resolve an internal `uses:` ref to its action.yml path.

    Returns (path, is_internal). External actions (actions/checkout@v4,
    docker/*, SonarSource/*, ...) return (None, False) and are skipped.
    """
    ref = str(ref)

    if ref.startswith("./"):
        # Local path relative to repo root (consumer-side). Best effort.
        base = os.path.join(REPO_ROOT, ref[2:])
    elif ref.startswith(GITHUB_INTERNAL_PREFIX):
        # jstrullu/cicd/<path>@<ref> -> <path> under REPO_ROOT.
        path = ref[len(GITHUB_INTERNAL_PREFIX):].split("@", 1)[0]
        base = os.path.join(REPO_ROOT, path)
    else:
        return None, False  # external action, not our contract

    for name in ("action.yml", "action.yaml"):
        cand = os.path.join(base, name)
        if os.path.isfile(cand):
            return cand, True
    return os.path.join(base, "action.yml"), True  # non-existent, for error message


def declared_github_inputs(action_path):
    """Return {name: {'required': bool, 'has_default': bool}} for an action.yml."""
    node = load_yaml(action_path)
    declared = {}
    if not isinstance(node, CommentedMap):
        return declared
    inputs = node.get("inputs")
    if isinstance(inputs, CommentedMap):
        for name, spec in inputs.items():
            required = False
            has_default = False
            if isinstance(spec, CommentedMap):
                required = bool(spec.get("required", False))
                has_default = "default" in spec
            declared[str(name)] = {"required": required, "has_default": has_default}
    return declared


def check_github_file(filepath):
    rel = os.path.relpath(filepath, REPO_ROOT)
    root = load_yaml(filepath)
    if root is None:
        return

    calls = []

    def visit(node):
        if "uses" in node:
            calls.append(node)

    walk(root, visit)

    for call in calls:
        ref = call["uses"]
        line = key_line(call, "uses")
        target, is_internal = resolve_github_action(ref)
        if not is_internal:
            continue  # external action — skip

        # G1 — reference resolves.
        if not os.path.isfile(target):
            errors.append(
                f"{rel}:{line} : action interne introuvable « {ref} »"
            )
            continue

        passed = call.get("with")
        passed_names = set()
        if isinstance(passed, CommentedMap):
            passed_names = {str(k) for k in passed.keys()}

        declared = declared_github_inputs(target)
        target_rel = os.path.relpath(target, REPO_ROOT)

        # G2 — unknown input passed.
        for name in passed_names:
            if name not in declared:
                pline = key_line(passed, name) if isinstance(passed, CommentedMap) else line
                errors.append(
                    f"{rel}:{pline} : input « {name} » passé à l'action "
                    f"« {target_rel} » mais non déclaré"
                )

        # G3 — required input (no default) not passed.
        for name, spec in declared.items():
            if spec["required"] and not spec["has_default"] and name not in passed_names:
                errors.append(
                    f"{rel}:{line} : input requis « {name} » de l'action "
                    f"« {target_rel} » non fourni"
                )


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #

def collect(root_dir):
    found = []
    for dirpath, _dirs, files in os.walk(root_dir):
        for name in files:
            if name.endswith((".yml", ".yaml")):
                found.append(os.path.join(dirpath, name))
    return sorted(found)


def main():
    azure_files = collect(AZURE_DIR)
    github_files = collect(GITHUB_DIR)

    for fp in azure_files:
        check_azure_file(fp)
    for fp in github_files:
        check_github_file(fp)

    total = len(azure_files) + len(github_files)
    print(
        f"Contrats analysés : {total} fichiers "
        f"({len(azure_files)} Azure, {len(github_files)} GitHub)."
    )

    if errors:
        print(f"\n{len(errors)} violation(s) de contrat :\n")
        for err in errors:
            print(f"  ✗ {err}")
        sys.exit(1)

    print("Aucune violation de contrat.")
    sys.exit(0)


if __name__ == "__main__":
    main()
