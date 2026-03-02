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
| `gitFlowType` | Git branching strategy (see below) | `github-flow` |
| `developIncrement` | Version bump for `develop` branch (gitflow only) | `patch` |
| `releaseIncrement` | Version bump for `release/*` branches (gitflow only) | `minor` |
| `hotfixIncrement` | Version bump for `hotfix/*` branches (gitflow only) | `patch` |
| `jsonFile` | Path to the version JSON file | `cicd.json` |
| `sonarKey` | SonarQube project key | - |
| `dockerRegistry` | Docker image repository name | - |
| `containerRegistry` | Azure DevOps service connection for Docker | - |
| `appName` | Application name (used for Kubernetes namespace) | `$(Build.Repository.Name)` |

## Git Flow Strategies

Set `gitFlowType` to choose how branches map to environments, versioning, and deployment:

### `github-flow` (default)

Simple flow: `main` + feature branches.

| Branch | Build & Test | Deploy | Tag | Version suffix |
|--------|:-----------:|:------:|:---:|:--------------:|
| `main`/`master` | Yes | production | Yes | - |
| Feature (PR) | Yes | - | - | - |

### `trunk-based`

Continuous deployment from a single main branch.

| Branch | Build & Test | Deploy | Tag | Version suffix |
|--------|:-----------:|:------:|:---:|:--------------:|
| `main`/`master` | Yes | production | Yes | - |
| Feature (PR) | Yes | - | - | - |

### `gitflow`

Structured promotion: `master` + `develop` + `release/*` + `hotfix/*`.

| Branch | Build & Test | Deploy | Tag | Version bump | Version suffix |
|--------|:-----------:|:------:|:---:|:------------:|:--------------:|
| `main`/`master` | Yes | production | Yes | none (from merge) | - |
| `develop` | Yes | dev | - | `developIncrement` | `-SNAPSHOT` |
| `release/*` | Yes | staging | Yes | `releaseIncrement` | `-rc` |
| `hotfix/*` | Yes | staging | Yes | `hotfixIncrement` | - |
| Feature (PR) | Yes | - | - | `versionIncrement` | - |

On `main`/`master`, no version bump occurs — the version comes from the merged `release` or `hotfix` branch. On environment branches like `staging` and `production` in gitlab-flow, the version also propagates without bumping.

### `gitlab-flow`

Environment branches with promotion: `main` → `staging` → `production`.

| Branch | Build & Test | Deploy | Tag | Version bump | Version suffix |
|--------|:-----------:|:------:|:---:|:------------:|:--------------:|
| `main`/`master` | Yes | dev | - | `versionIncrement` | - |
| `staging` | Yes | staging | - | none (from main) | - |
| `production` | Yes | production | Yes | none (from main) | - |
| Feature (PR) | Yes | - | - | `versionIncrement` | - |

### Version Increment Priority

The version bump level is resolved in this order (highest priority first):

1. **PR title** — `#VERSION MAJOR/MINOR/PATCH` in the PR title always wins
2. **Branch-specific default** — `developIncrement`, `releaseIncrement`, or `hotfixIncrement` for gitflow branches
3. **Pipeline parameter** — the `versionIncrement` parameter (default: `patch`)
4. **`none`** — some branches skip bumping entirely (e.g., `master` in gitflow, `staging`/`production` in gitlab-flow)

### Usage Example

```yaml
stages:
  - template: azure-pipelines/pipelines/java_gradle_pipeline.yml@templates
    parameters:
      gitFlowType: 'gitflow'
      versionIncrement: 'patch'
      sonarKey: 'my-project'
      javaVersion: '17'
      dockerRegistry: 'my-app'
      containerRegistry: 'my-registry-connection'
```

The initialization stage resolves the git flow context and exposes output variables (`shouldDeploy`, `deployEnvironment`, `shouldTag`, `shouldFinalize`, `versionSuffix`) that downstream stages use to decide what to run.

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
