# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This is a shared CI/CD template library providing reusable pipeline templates for Azure DevOps and GitHub Actions. Consumer repositories reference these templates to build their pipelines. There is no buildable application code here — only YAML pipeline definitions.

## Repository Structure

```
azure-pipelines/
  pipelines/   → Top-level pipeline definitions (entry points consumed by other repos)
  jobs/        → Reusable job templates, organized by tech stack
  steps/       → Reusable step templates (versioning helpers)
github-actions/
  actions/     → GitHub Actions workflow definitions (WIP, only .NET Core started)
  jobs/        → Reusable job templates for GitHub Actions
```

## Architecture

### Azure Pipelines (main focus)

All pipelines follow a common stage sequence:

1. **Initialisation** — Semantic version bump via `json_semantic_version.yml`. Reads/creates a `cicd.json` file in the consumer repo, bumps the version using the `semver` npm package, and outputs `DockerTag` for downstream stages.
2. **Build & Test** — Language-specific build, test, and SonarQube analysis.
3. **Docker Build & Publish** / **Deploy** — Optional stages, skipped on PRs (`ne(variables['Build.Reason'], 'PullRequest')`).
4. **Finalisation** — Writes the new version to `cicd.json`, commits with `***NO_CI***` prefix (to avoid CI loops), creates a git tag (`branch-version`), and pushes.

### Version Bump Override

The `set_version_increment` step inspects the PR title for a `#VERSION` keyword (e.g., `#VERSION major`) to override the default `patch` increment.

### Supported Tech Stacks

| Stack | Pipeline | Jobs |
|-------|----------|------|
| .NET Core | `dotnetcore_pipeline.yml` | `dotnetcore_build_test.yml`, `security_checks.yml` (Snyk) |
| Java/Gradle | `java_gradle_pipeline.yml` | `java_gradle_test_and_build.yml`, `docker_build_and_publish.yml`, `kube_deploy.yml` |
| Java/Gradle Avro | `java_gradle_avro_pipeline.yml` | `java_gradle_avro_build.yml`, `gradle_package_publish.yml` |
| Angular/npm | `angular_npm_pipeline.yml` | `angular_test_and_build.yml`, `angular_linter.yml` |
| Flutter | `flutter_pipeline.yml` | `flutter_version_increment.yml`, `flutter_build_test.yml`, `flutter_build_firebase_deploy.yml` |

### Cross-cutting jobs

- `docker_build_and_publish.yml` — Builds and pushes Docker images to a registry.
- `kube_deploy.yml` — Deploys to Kubernetes using manifests from the consumer repo's `.kube/` directory with token replacement.
- `finalisation.yml` — Language-aware version commit and git tag push. Handles Angular (`npm version`), .NET (`AssemblyVersion` in .csproj), and Java/Flutter (via `cicd.json` only).

## Conventions

- **Language**: Display names and comments are in French.
- **Template references**: Pipelines use absolute paths from repo root (`/jobs/...`). Job templates reference steps with relative paths (`..\..\steps\...`).
- **Version persistence**: All stacks (except Flutter, which uses `pubspec.yaml` via Cider) store version in `cicd.json` at the consumer repo root.
- **PR builds**: Docker, deploy, and finalisation stages are conditionally skipped for pull request builds.
- **SonarQube**: Integrated into all build jobs. Some Angular/Flutter Sonar tasks are currently commented out.
- **Node.js 18.x** is used across all stacks that need Node.
- **GitHub Actions**: Currently incomplete — only a skeleton for .NET Core exists under `github-actions/`.
