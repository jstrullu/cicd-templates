# CI/CD Pipeline Templates

Reusable CI/CD pipeline templates for **Azure Pipelines** and **GitHub Actions**, supporting multiple technology stacks with built-in semantic versioning, code quality scanning, and multi-stage deployments.

## Supported Stacks

| Stack | Pipeline | Build & Test | Docker | Kubernetes | SonarQube |
|-------|----------|-------------|--------|------------|-----------|
| .NET Core | `dotnetcore_pipeline.yml` | Yes | - | - | Yes |
| Java/Gradle | `java_gradle_pipeline.yml` | Yes | Yes | Yes | Yes |
| Java/Gradle (Avro) | `java_gradle_avro_pipeline.yml` | Yes | - | - | - |
| Angular/npm | `angular_npm_pipeline.yml` | Yes | Yes | Yes | Optional |
| Flutter | `flutter_pipeline.yml` | Yes | - | Firebase | Yes |

## Repository Structure

```
├── azure-pipelines/
│   ├── pipelines/       # Main pipeline definitions (entry points)
│   ├── jobs/            # Reusable job templates
│   │   ├── angular/
│   │   ├── dotnetcore/
│   │   ├── flutter/
│   │   └── java/
│   └── steps/           # Reusable step templates
└── github-actions/      # GitHub Actions workflows (early stage)
    ├── actions/
    └── jobs/
```

## How It Works

Each pipeline follows a common multi-stage pattern:

1. **Initialization** — Semantic version bump based on PR title (`#VERSION MAJOR/MINOR/PATCH`)
2. **Build & Test** — Language-specific compilation, testing, and code analysis
3. **Docker Build & Publish** — Containerization (skipped on PRs)
4. **Deploy** — Kubernetes or Firebase deployment (skipped on PRs)
5. **Finalization** — Git commit and tag with the new version

### Semantic Versioning

Version bumps are driven by PR titles. Include `#VERSION MAJOR`, `#VERSION MINOR`, or `#VERSION PATCH` in your PR title to control the bump level. Defaults to `patch` if not specified.

Versions are stored in a JSON file (`cicd.json` by default) and tagged in git as `branch-major.minor.patch`.

## Usage

Reference the templates from your project's pipeline definition:

```yaml
# azure-pipelines.yml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: your-org/cicd

stages:
  - template: azure-pipelines/pipelines/dotnetcore_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      sonarKey: 'your-project-key'
      projectFile: 'src/YourProject.csproj'
      jsonFile: 'cicd.json'
```

## Parameters

Most templates accept these common parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `versionIncrement` | Default bump level (`major`, `minor`, `patch`) | `patch` |
| `jsonFile` | Path to the version JSON file | `cicd.json` |
| `sonarKey` | SonarQube project key | - |
| `dockerRegistry` | Docker image repository name | - |
| `containerRegistry` | Azure DevOps service connection for Docker | - |
| `appName` | Application name (used for Kubernetes namespace) | `$(Build.Repository.Name)` |

## Service Connections

The templates reference the following Azure DevOps service connections that you need to configure in your organization:

| Connection | Used by | Purpose |
|------------|---------|---------|
| SonarQube (`sonarConnection`) | Build jobs | Code quality analysis |
| Docker registry (`containerRegistry`) | Docker jobs | Container image push |
| Repos (`reposConnection`) | Version increment | PR title parsing via API |
| Snyk (`snykConnection`) | Security checks | Dependency vulnerability scanning |

All connection names are parameterized with sensible defaults.

## License

[MIT](LICENSE)
