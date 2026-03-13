---
paths:
  - "azure-pipelines/jobs/json_semantic_version.yml"
  - "azure-pipelines/jobs/finalisation.yml"
  - "azure-pipelines/steps/**"
  - "github-actions/actions/semantic-version/**"
  - "github-actions/actions/finalisation/**"
  - "github-actions/actions/set-version-file/**"
---

# Semantic Versioning System

## Flow

1. **Read** — `cicd.json` from consumer repo root: `{"version": "1.2.3"}`
2. **Check override** — PR title scanned for `#VERSION MAJOR/MINOR/PATCH`
3. **Bump** — `semver` npm CLI increments version
4. **Output** — `DockerTag` variable available to all downstream stages
5. **Finalize** — Write new version back, commit with `***NO_CI***`, create git tag

## cicd.json (Consumer Contract)

Every consumer repo MUST have `cicd.json` at root:
```json
{"version": "0.0.0"}
```

## Git Flow Context

`resolve_gitflow_context.yml` determines:
- `shouldDeploy` — Whether to run Docker/K8s stages
- `deployEnvironment` — Target: dev, staging, production
- `shouldTag` — Whether to create git tag
- `shouldFinalize` — Whether to commit version + push

Based on branch + gitFlowType parameter (github-flow, gitflow, trunk-based, gitlab-flow).

## Language-Aware Finalization

Version is also updated in language-specific files:
- **.NET**: `<AssemblyVersion>` in .csproj
- **Node.js/Angular**: `npm version` (updates package.json)
- **Python**: pyproject.toml / setup.cfg / setup.py (sed replacement)
- **Maven**: `mvn versions:set` (updates pom.xml)
- **Flutter/Go/Java Gradle**: cicd.json only

## Git Tag Format

`{branch}-{major}.{minor}.{patch}` — e.g., `master-1.2.3`, `develop-1.3.0-rc.1`
