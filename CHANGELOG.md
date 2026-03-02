# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Configurable git flow strategies (`github-flow`, `gitflow`, `trunk-based`, `gitlab-flow`) via `gitFlowType` pipeline parameter
- Branch-specific version increments for gitflow (`developIncrement`, `releaseIncrement`, `hotfixIncrement`)
- `resolve_gitflow_context.yml` step template that outputs deployment, tagging, and versioning decisions
- Version suffix support for pre-release builds (`-SNAPSHOT`, `-rc`)
- `none` version increment for promotion branches (gitflow `master`, gitlab-flow `staging`/`production`)
- Dynamic deploy environment selection based on git flow context
- `shouldTag` parameter on `finalisation.yml` for conditional tagging
- Community files: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, issue and PR templates
- MIT LICENSE, README.md, .gitignore

### Changed
- All pipeline stage conditions now use git flow context outputs instead of hardcoded PR checks
- Docker registry connection parameterized (`containerRegistry`) — was hardcoded
- Insecure registry URL parameterized (`insecureRegistryUrl`) — was hardcoded
- All service connection names parameterized with defaults (`sonarConnection`, `snykConnection`, `reposConnection`)
- Kubernetes resource/namespace uses `appName` parameter — was hardcoded
- Deploy stage renamed from `Deploy_To_Dev` to `Deploy` with dynamic environment
- Git user email/name replaced with generic `ci-service@example.com`

### Removed
- Hardcoded internal IP address from Docker build job
- Hardcoded company email addresses
- Hardcoded internal project names

## [0.1.0] - Initial release

### Added
- Azure Pipelines templates for .NET Core, Java/Gradle, Java/Gradle Avro, Angular/npm, and Flutter
- Semantic versioning with JSON file storage and PR title parsing (`#VERSION MAJOR/MINOR/PATCH`)
- Docker build and publish job template
- Kubernetes deployment job template
- SonarQube integration across all language templates
- Snyk security scanning for .NET Core
- Flutter-specific versioning with Cider and Firebase deployment
- Multi-stage pipeline pattern: Initialization, Build & Test, Docker, Deploy, Finalization
