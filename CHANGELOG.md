# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.1] - 2026-03-03

### Added
- Add GitHub Actions CI and auto-changelog workflows
- Add mutation testing support for all languages
- Add Docker build and Kubernetes deploy stages to .NET Core pipeline
- adding more languages
- Add Java Maven pipeline template
- Add Go pipeline template
- Add Node.js/TypeScript pipeline template
- Add Python pipeline template
- Add community and governance files for public repository
- Add per-branch version increment for each git flow strategy
- Add configurable git flow strategy to initialization stage

### Changed
- Port Azure Pipelines templates to GitHub Actions
- Merge pull request #6 from jstrullu/claude/read-code-init-memory-MOceZ
- Replace expression with GITHUB_BASE_REF env var in CI workflow
- Merge pull request #5 Add GitHub Actions CI and auto-changelog workflows
- Merge pull request #4
- Move Finalization stage after Deploy in all pipelines
- Skip SonarQube steps when sonarKey is not provided
- turning into public repo
- Prepare repository for public release
- Merge pull request #1 from jstrullu/claude/read-code-init-memory-MOceZ
- Translate French variable names, identifiers, and comments to English
- démarrage github
- creation du dossier azure pipelines

### Fixed
- Fix CI workflow by moving sed logic to external script
- Fix GitHub Actions workflow expression parsing error

### Documentation
- auto-update CHANGELOG.md [skip ci]
- auto-update CHANGELOG.md [skip ci]


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
