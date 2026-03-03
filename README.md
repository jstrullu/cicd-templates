# CI/CD Pipeline Templates

Reusable CI/CD pipeline templates for **Azure Pipelines** and **GitHub Actions**, supporting multiple technology stacks with built-in semantic versioning, code quality scanning, and multi-stage deployments.

## Supported Stacks

| Stack | Azure Pipelines | GitHub Actions | Build & Test | Docker | Kubernetes | SonarQube | Security (Snyk) |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| .NET Core | Yes | Yes | Yes | Yes | Yes | Optional | Optional |
| Java/Gradle | Yes | Yes | Yes | Yes | Yes | Optional | Optional |
| Java/Gradle (Avro) | Yes | Yes | Yes | - | - | - | Optional |
| Angular/npm | Yes | Yes | Yes | Yes | Yes | Optional | Optional |
| Flutter | Yes | Yes | Yes | - | Firebase | Optional | Optional |
| Go | Yes | Yes | Yes | Yes | Yes | Optional | Optional |
| Java/Maven | Yes | Yes | Yes | Yes | Yes | Optional | Optional |
| Node.js/TypeScript | Yes | Yes | Yes | Yes | Yes | Optional | Optional |
| Python | Yes | Yes | Yes | Yes | Yes | Optional | Optional |

## Repository Structure

```
├── .github/workflows/       # CI, changelog, and release workflows for this repo
├── azure-pipelines/
│   ├── pipelines/           # Main pipeline definitions (entry points)
│   ├── jobs/                # Reusable job templates
│   │   ├── angular/
│   │   ├── dotnetcore/
│   │   ├── flutter/
│   │   ├── go/
│   │   ├── java/
│   │   ├── node/
│   │   └── python/
│   └── steps/               # Reusable step templates
├── github-actions/
│   ├── actions/             # Composite actions (reusable building blocks)
│   │   ├── angular/
│   │   ├── docker-build-push/
│   │   ├── dotnetcore/
│   │   ├── finalisation/
│   │   ├── flutter/
│   │   ├── go/
│   │   ├── java/
│   │   ├── kube-deploy/
│   │   ├── node/
│   │   ├── python/
│   │   ├── semantic-version/
│   │   └── set-version-file/
│   └── workflow-templates/  # Full pipeline workflow templates
└── scripts/                 # Helper scripts (changelog, linting, validation)
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

## Getting Started

1. Create a `cicd.json` file at the root of your consumer repository:
   ```json
   {"version": "0.0.0"}
   ```
2. Choose your platform (Azure Pipelines or GitHub Actions) and tech stack.
3. Configure your pipeline using the examples below or the [detailed consumer examples](docs/consumer-example.md).

## Usage

### Azure Pipelines

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

### GitHub Actions

Copy a workflow template from `github-actions/workflow-templates/` into your repo's `.github/workflows/` directory and configure the `env` variables:

```yaml
# .github/workflows/pipeline.yml — copied from github-actions/workflow-templates/dotnetcore_pipeline.yml
env:
  VERSION_INCREMENT: 'patch'
  SONAR_KEY: 'your-project-key'
  PROJECT_FILE: 'src/YourProject.csproj'
  FICHIER_JSON: 'cicd.json'
```

The workflow templates reference composite actions from this repository (e.g. `jstrullu/cicd/github-actions/actions/semantic-version@master`).

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
| `sonarKey` | SonarQube project key (empty = disabled) | `''` |
| `enableSecurityChecks` | Enable Snyk security scanning stage | `false` |
| `securityTargetFile` | Target file for Snyk (e.g. `go.mod`, `package.json`) | stack-specific |
| `enableMutationTesting` | Enable mutation testing stage | `false` |
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

## Repository CI/CD

This repository has its own GitHub Actions workflows:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI** (`ci.yml`) | Push to master, PRs | YAML linting, template validation, changelog check |
| **Update Changelog** (`changelog.yml`) | Push to master | Auto-generates the `[Unreleased]` section from commit history |
| **Release** (`release.yml`) | Tag push (`v*`, `*.*.*`) | Freezes changelog, creates a GitHub Release with release notes |

The changelog and release workflows share a concurrency group to prevent race conditions when a commit and tag are pushed together.

## Documentation

- [Consumer Repository Examples](docs/consumer-example.md) — Detailed per-stack setup examples
- [Troubleshooting Guide](docs/troubleshooting.md) — Common issues and solutions
- [Migration Guide: Azure to GitHub](docs/migration-azure-to-github.md) — Step-by-step migration checklist

## License

[MIT](LICENSE)
