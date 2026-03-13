# CLAUDE.md — CI/CD Templates

Shared, reusable CI/CD template library for Azure DevOps and GitHub Actions. 9 technology stacks, 5-stage pipeline pattern. No application code — only YAML pipeline definitions.

## Supported Stacks

.NET Core, Java/Gradle, Java/Gradle Avro, Java/Maven, Angular/npm, Flutter, Go, Node.js/TypeScript, Python

## Structure

```
azure-pipelines/
  pipelines/    → 9 entry-point pipeline templates (consumed by other repos)
  jobs/         → Language-specific + cross-cutting job templates
  steps/        → Reusable step templates (versioning, git flow context)
github-actions/
  actions/              → Composite actions (building blocks per stack)
  workflow-templates/   → Full pipeline workflows (copied into consumer repos)
scripts/                → lint_yaml.sh, validate_templates.py, changelog scripts
docs/                   → consumer-example.md, migration guide, troubleshooting
```

## Pipeline Architecture — 5-Stage Pattern

1. **Initialization** — Semantic version bump via `cicd.json` + `semver` npm. PR title `#VERSION MAJOR/MINOR/PATCH` overrides default.
2. **Build & Test** — Language-specific: restore, compile, test (coverage), SonarQube (optional).
3. **Security Checks** (optional) — Snyk scanning when `enableSecurityChecks=true`.
4. **Docker Build & Publish** (conditional) — Skipped on PRs. Builds image, pushes with semver tag.
5. **Finalization** (conditional) — Updates version file, commits with `***NO_CI***`, creates git tag, pushes.

**Git Flow Strategies:** github-flow, trunk-based, gitflow, gitlab-flow. Resolved by `resolve_gitflow_context.yml`.

## Commands (repo self-CI)

```bash
# Lint YAML
bash scripts/lint_yaml.sh

# Validate templates
python3 scripts/validate_templates.py

# Generate changelog
python3 scripts/generate_changelog.py
```

## Key Design Decisions

- **Zero hardcoded values**: No internal IPs, no org-specific secrets. `validate_templates.py` enforces this.
- **Consumer contract**: Provide `cicd.json` (`{"version": "0.0.0"}`) at repo root.
- **Language-aware finalization**: npm version (.NET .csproj, Node package.json, Python pyproject.toml, Maven pom.xml).
- **PR-aware conditionals**: Docker/deploy/finalize skip on pull requests.
- **French display names**: All step/job display names and comments in French.
- **Cross-platform parity**: Azure Pipelines (primary) + GitHub Actions (full port) for all 9 stacks.
- **Mutation testing**: Optional per stack (Stryker.NET, Stryker JS, PIT Java).

## Claude Code Workflow

1. **Planning**: Identify which stack and platform (Azure/GitHub) is affected
2. **Implementation**: Follow YAML conventions, maintain cross-platform parity
3. **Verification**: `bash scripts/lint_yaml.sh && python3 scripts/validate_templates.py`

### Contextual Rules

`.claude/rules/` auto-load by path:
- `azure-pipelines.md` — Azure template conventions, parameter patterns, path references
- `github-actions.md` — Composite actions, workflow templates, input conventions
- `versioning.md` — Semantic versioning flow, cicd.json, finalization patterns

### Custom Agents

- **`add-stack`** — Add support for a new technology stack (both Azure + GitHub Actions)
- **`add-stage`** — Add a new pipeline stage to existing stack

## Conventions

- YAML: 2-space indent, max 250 chars/line (yamllint enforced)
- Azure template refs: absolute paths in pipelines (`/jobs/...`), relative in jobs (`..\..\steps\...`)
- GitHub Actions inputs: kebab-case (`sonar-project-key`)
- Azure parameters: camelCase (`sonarProjectKey`)
- All descriptions and display names in French
- Conventional commits required for contributions
