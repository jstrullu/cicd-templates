# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.2] - 2026-03-03

### Added
- add dependency caching, timeouts, mutation testing parity, and artifact retention


## [0.7.0] - 2026-03-03

### Added
- Add `enableSecurityChecks` parameter to dotnetcore, flutter, and java_gradle_avro pipelines
- Create flutter/security_checks.yml job template (Snyk)
- Uncomment and conditionally enable SonarQube in Angular build template

### Changed
- Update Angular jobs from Node.js 18.x to 20.x
- Remove `continueOnError` from .NET SonarQube tasks for consistency with other stacks

## [0.6.1] - 2026-03-03

### Added
- Make SonarQube steps optional in dotnetcore and flutter GitHub Actions

### Changed
- Use PAT_TOKEN to bypass branch protection in changelog workflows

## [0.6.0] - 2026-03-03

### Added
- Complete GitHub Actions parity with Azure Pipelines for all 9 stacks
- Add security checks (Snyk) to all language pipelines
- Add parameterizable git user email/name for finalization

### Fixed
- Use GitHub Contents API to bypass branch protection in CI workflows
- Release workflow uses direct push with admin bypass for changelog freeze

## [0.5.1] - 2026-03-03

### Documentation
- Update README with new stacks, GitHub Actions usage, and repo CI/CD

## [0.5.0] - 2026-03-03

### Added
- Add release workflow and changelog freeze script

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
- GitHub Actions CI and auto-changelog workflows
- Mutation testing support for all languages
- Per-branch version increment for each git flow strategy
- Configurable git flow strategy (github-flow, gitflow, trunk-based, gitlab-flow)
- Port Azure Pipelines templates to GitHub Actions
- Add community and governance files for public repository
