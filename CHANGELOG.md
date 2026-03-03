# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- use PAT_TOKEN to bypass branch protection in changelog workflows


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
