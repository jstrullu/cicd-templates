# Consumer Repository Examples

This guide shows how to integrate the CI/CD templates into your project.

## Prerequisites

1. Create a `cicd.json` file at the root of your repository:

```json
{"version": "0.0.0"}
```

2. Choose your platform (Azure Pipelines or GitHub Actions) and tech stack.

## Directory Structure

A consumer repository typically looks like this:

```
my-project/
├── cicd.json                    # Version tracking (auto-managed)
├── azure-pipelines.yml          # Azure Pipelines config (if using Azure)
├── .github/workflows/
│   └── pipeline.yml             # GitHub Actions config (if using GH Actions)
├── .kube/                       # Kubernetes manifests (if deploying to k8s)
│   ├── deployment.yml
│   └── service.yml
├── Dockerfile                   # Docker build (if containerizing)
└── src/                         # Your application code
```

---

## Azure Pipelines Examples

Reference the templates from your `azure-pipelines.yml`:

### .NET Core

```yaml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection  # Your GitHub service connection

stages:
  - template: azure-pipelines/pipelines/dotnetcore_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      sonarKey: 'my-dotnet-project'
      projectFile: 'src/MyApp/MyApp.csproj'
      securityTargetDir: 'src/MyApp'
      jsonFile: 'cicd.json'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-docker-connection'
```

**Docker push mode.** By default (`dockerPushMode: 'service-connection'`),
this uses the `Docker@2` task and requires the `containerRegistry` service
connection above. For an in-cluster/self-hosted registry with no service
connection (matches every real consumer pipeline in the org's portfolio),
switch to `insecure-cli`:

```yaml
    parameters:
      dockerPushMode: 'insecure-cli'
      dockerRegistry: 'registry.internal:5000'
      dockerImageName: 'my-app'             # defaults to appName if omitted
      insecureRegistryUrl: 'registry.internal:5000'  # configures /etc/docker/daemon.json, leave empty if the agent is already configured
      dockerAlsoTagLatest: true             # default
      dockerBuildArgs: |                    # optional, one KEY=VALUE per line
        PUBLIC_GA_ID=G-XXXXXXX
        PUBLIC_SITE_URL=$(PUBLIC_SITE_URL)
      # containerRegistry no longer required in this mode
```

**Multiple images from one repo** (e.g. API + Worker + Frontend, or one
Dockerfile built twice with different `--target`). Set `dockerImages` — when
non-empty it takes over from `dockerImageName`, one image per entry, each
named `{appName}-{item.name}`:

```yaml
    parameters:
      dockerPushMode: 'insecure-cli'
      dockerRegistry: 'registry.internal:5000'
      dockerImages:
        - name: api
          dockerfile: src/Api/Dockerfile
          context: .
        - name: frontend
          dockerfile: src/Frontend/Dockerfile
          context: src/Frontend
        # Single Dockerfile, two build targets (e.g. ShopTemplate):
        # - name: api
        #   dockerfile: Dockerfile
        #   target: api
        # - name: frontend
        #   dockerfile: Dockerfile
        #   target: frontend
        #   buildArgs: |
        #     VITE_API_URL=$(SANDBOX_API_URL)
```

**Deploy mode.** By default (`deployMode: 'kube-manifest'`), this uses the
`KubernetesManifest@0` task and needs a Kubernetes-type Azure DevOps
environment resource. For an agent already running inside the target
cluster (matches every real consumer pipeline in the org's portfolio),
switch to `helm`:

```yaml
    parameters:
      deployMode: 'helm'
      helmChartPath: 'helm/my-app'
      helmValuesFile: 'helm/my-app/values-production.yaml'
      helmSetValues: |
        secrets.postgresPassword=$(POSTGRES_PASSWORD)
        secrets.apiKey=$(API_KEY)
```

**Staged Sandbox → Prod deploy** (helm mode only). Deploys to a sandbox
namespace automatically, then pauses for manual approval before deploying
the same image tag to production. Configure the approval check on
`prodApprovalEnvironment` in **Pipelines → Environments → &lt;name&gt; →
Approvals and checks** — the pipeline has no opinion on who approves.

```yaml
    parameters:
      deployMode: 'helm'
      enableStagedDeploy: true
      helmChartPath: 'helm/my-app'
      helmValuesFile: 'helm/my-app/values-production.yaml'   # used for Prod
      helmSetValues: |
        secrets.postgresPassword=$(POSTGRES_PASSWORD)
      sandboxHelmValuesFile: 'helm/my-app/values-sandbox.yaml'  # defaults to helmValuesFile if omitted
      sandboxHelmSetValues: |
        secrets.postgresPassword=$(SANDBOX_POSTGRES_PASSWORD)
      # sandboxNamespace: 'my-app-staging'   # defaults to '{appName}-sandbox'
      prodApprovalEnvironment: 'my-app-prod'   # required
```

### Java/Gradle

```yaml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/java_gradle_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      sonarKey: 'my-java-project'
      javaVersion: '17'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-docker-connection'
```

### Java/Maven

```yaml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/java_maven_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      sonarKey: 'my-maven-project'
      javaVersion: '17'
      pomFile: 'pom.xml'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-docker-connection'
```

### Python

```yaml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/python_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      sonarKey: 'my-python-project'
      pythonVersion: '3.12'
      requirementsFile: 'requirements.txt'
      testDirectory: 'tests'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-docker-connection'
```

### Go

```yaml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/go_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      sonarKey: 'my-go-project'
      goVersion: '1.22'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-docker-connection'
```

### Node.js/TypeScript

```yaml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/node_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      sonarKey: 'my-node-project'
      nodeVersion: '20.x'
      packageManager: 'npm'
      buildScript: 'build'
      testScript: 'test'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-docker-connection'
```

### Angular

```yaml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/angular_npm_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      sonarKey: 'my-angular-project'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-docker-connection'
```

### Astro

Astro sites in the portfolio typically don't ship unit tests — `enableTests`
stays `false` unless the project has added one (Vitest, etc.).

```yaml
trigger:
  - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/astro_pipeline.yml@templates
    parameters:
      versionIncrement: 'patch'
      typecheckScript: 'typecheck'   # runs `astro check`
      buildScript: 'build'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-docker-connection'
```

---

## GitLab CI Example

**Status: early / structurally verified only, not yet run against a real GitLab runner** (no GitLab account/runner available at the time of writing — see CICD-2 through CICD-5). .NET build + test only; Docker, deploy, and versioning are separate future tickets, not covered here.

```yaml
# .gitlab-ci.yml
include:
  - project: 'jstrullu/cicd-templates'
    ref: main
    file: 'gitlab-ci/dotnet_pipeline.yml'
    inputs:
      dotnetSdkVersion: '10.0'   # optional, defaults to '10.0'

stages:
  - build
  - test
```

## GitHub Actions Examples

Copy a workflow template from `github-actions/workflow-templates/` into your `.github/workflows/` directory and edit the `env` section.

### .NET Core

```yaml
# .github/workflows/pipeline.yml
name: .NET Core Pipeline

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

env:
  VERSION_INCREMENT: 'patch'
  SONAR_KEY: 'my-dotnet-project'
  SECURITY_TARGET_FILE: 'MyApp.sln'
  PROJECT_FILE: 'src/MyApp/MyApp.csproj'
  FICHIER_JSON: 'cicd.json'

jobs:
  initialisation:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.versioning.outputs.version }}
      docker-tag: ${{ steps.versioning.outputs.docker-tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Versionnement sémantique
        id: versioning
        uses: jstrullu/cicd-templates/github-actions/actions/semantic-version@master
        with:
          version-increment: ${{ env.VERSION_INCREMENT }}
          fichier-json: ${{ env.FICHIER_JSON }}

  build-and-test:
    runs-on: ubuntu-latest
    needs: initialisation
    steps:
      - uses: actions/checkout@v4
      - name: Build & Test .NET Core
        uses: jstrullu/cicd-templates/github-actions/actions/dotnetcore/build-test@master
        with:
          sonar-project-key: ${{ env.SONAR_KEY }}
          project-file: ${{ env.PROJECT_FILE }}
          project-version: ${{ needs.initialisation.outputs.version }}
          sonar-host-url: ${{ secrets.SONAR_HOST_URL }}
          sonar-token: ${{ secrets.SONAR_TOKEN }}

  finalisation:
    runs-on: ubuntu-latest
    needs: [initialisation, build-and-test]
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Finalisation
        uses: jstrullu/cicd-templates/github-actions/actions/finalisation@master
        with:
          release-version: ${{ needs.initialisation.outputs.version }}
          fichier-json: ${{ env.FICHIER_JSON }}
          language: '.net'
          project-file: ${{ env.PROJECT_FILE }}
```

### Python

```yaml
# .github/workflows/pipeline.yml
name: Python Pipeline

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

env:
  VERSION_INCREMENT: 'patch'
  SONAR_KEY: 'my-python-project'
  PYTHON_VERSION: '3.12'
  REQUIREMENTS_FILE: 'requirements.txt'
  TEST_DIRECTORY: 'tests'
  FICHIER_JSON: 'cicd.json'
  DOCKER_REGISTRY: 'ghcr.io/my-org'

jobs:
  initialisation:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.versioning.outputs.version }}
      docker-tag: ${{ steps.versioning.outputs.docker-tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - id: versioning
        uses: jstrullu/cicd-templates/github-actions/actions/semantic-version@master
        with:
          version-increment: ${{ env.VERSION_INCREMENT }}
          fichier-json: ${{ env.FICHIER_JSON }}

  build-and-test:
    runs-on: ubuntu-latest
    needs: initialisation
    steps:
      - uses: actions/checkout@v4
      - uses: jstrullu/cicd-templates/github-actions/actions/python/build-test@master
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          requirements-file: ${{ env.REQUIREMENTS_FILE }}
          test-directory: ${{ env.TEST_DIRECTORY }}
          project-version: ${{ needs.initialisation.outputs.version }}
          sonar-key: ${{ env.SONAR_KEY }}
          sonar-host-url: ${{ secrets.SONAR_HOST_URL }}
          sonar-token: ${{ secrets.SONAR_TOKEN }}

  finalisation:
    runs-on: ubuntu-latest
    needs: [initialisation, build-and-test]
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: jstrullu/cicd-templates/github-actions/actions/finalisation@master
        with:
          release-version: ${{ needs.initialisation.outputs.version }}
          fichier-json: ${{ env.FICHIER_JSON }}
          language: 'python'
```

### Go

```yaml
# .github/workflows/pipeline.yml
name: Go Pipeline

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

env:
  VERSION_INCREMENT: 'patch'
  SONAR_KEY: 'my-go-project'
  GO_VERSION: '1.22'
  FICHIER_JSON: 'cicd.json'
  DOCKER_REGISTRY: 'ghcr.io/my-org'

jobs:
  initialisation:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.versioning.outputs.version }}
      docker-tag: ${{ steps.versioning.outputs.docker-tag }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - id: versioning
        uses: jstrullu/cicd-templates/github-actions/actions/semantic-version@master
        with:
          version-increment: ${{ env.VERSION_INCREMENT }}
          fichier-json: ${{ env.FICHIER_JSON }}

  build-and-test:
    runs-on: ubuntu-latest
    needs: initialisation
    steps:
      - uses: actions/checkout@v4
      - uses: jstrullu/cicd-templates/github-actions/actions/go/build-test@master
        with:
          go-version: ${{ env.GO_VERSION }}
          project-version: ${{ needs.initialisation.outputs.version }}
          sonar-key: ${{ env.SONAR_KEY }}
          sonar-host-url: ${{ secrets.SONAR_HOST_URL }}
          sonar-token: ${{ secrets.SONAR_TOKEN }}

  finalisation:
    runs-on: ubuntu-latest
    needs: [initialisation, build-and-test]
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: jstrullu/cicd-templates/github-actions/actions/finalisation@master
        with:
          release-version: ${{ needs.initialisation.outputs.version }}
          fichier-json: ${{ env.FICHIER_JSON }}
          language: 'go'
```

### Astro

Copy `github-actions/workflow-templates/astro_pipeline.yml` into your
`.github/workflows/` directory and edit the `env` section. No Docker/deploy
stages by default (most Astro sites in the portfolio are static or served
via a lightweight adapter) — extend the copied file if you need them.

```yaml
# .github/workflows/pipeline.yml
name: Astro Pipeline

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

env:
  VERSION_INCREMENT: 'patch'
  NODE_VERSION: '20'
  PACKAGE_MANAGER: 'npm'
  TYPECHECK_SCRIPT: 'typecheck'   # runs `astro check`
  BUILD_SCRIPT: 'build'
  FICHIER_JSON: 'cicd.json'

jobs:
  initialisation:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.versioning.outputs.version }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - id: versioning
        uses: jstrullu/cicd-templates/github-actions/actions/semantic-version@master
        with:
          version-increment: ${{ env.VERSION_INCREMENT }}
          fichier-json: ${{ env.FICHIER_JSON }}

  build-and-typecheck:
    runs-on: ubuntu-latest
    needs: initialisation
    steps:
      - uses: actions/checkout@v4
      - uses: jstrullu/cicd-templates/github-actions/actions/astro/build-test@master
        with:
          node-version: ${{ env.NODE_VERSION }}
          package-manager: ${{ env.PACKAGE_MANAGER }}
          typecheck-script: ${{ env.TYPECHECK_SCRIPT }}
          build-script: ${{ env.BUILD_SCRIPT }}
          project-version: ${{ needs.initialisation.outputs.version }}
          fichier-json: ${{ env.FICHIER_JSON }}

  finalisation:
    runs-on: ubuntu-latest
    needs: [initialisation, build-and-typecheck]
    if: github.event_name != 'pull_request'
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: jstrullu/cicd-templates/github-actions/actions/finalisation@master
        with:
          release-version: ${{ needs.initialisation.outputs.version }}
          fichier-json: ${{ env.FICHIER_JSON }}
          language: 'node'
```

---

## PR Title Version Override

Control the version bump level by including a keyword in your PR title:

| PR Title | Bump |
|----------|------|
| `feat: add login page` | `patch` (default) |
| `feat: add login page #VERSION minor` | `minor` |
| `feat!: redesign API #VERSION major` | `major` |

The keyword is case-insensitive: `#VERSION MAJOR`, `#version Major`, and `#Version major` all work.

---

## Git Flow Strategy Examples

### github-flow (default)

Simple flow — all commits to `master` trigger the full pipeline:

```yaml
# Azure Pipelines
parameters:
  gitFlowType: 'github-flow'
  versionIncrement: 'patch'
```

### gitflow

Structured branching with `develop`, `release/*`, and `hotfix/*`:

```yaml
# Azure Pipelines
parameters:
  gitFlowType: 'gitflow'
  versionIncrement: 'patch'
  developIncrement: 'patch'      # bump level for develop branch
  releaseIncrement: 'minor'      # bump level for release/* branches
  hotfixIncrement: 'patch'       # bump level for hotfix/* branches
```

### gitlab-flow

Environment-based promotion (`main` → `staging` → `production`):

```yaml
# Azure Pipelines
parameters:
  gitFlowType: 'gitlab-flow'
  versionIncrement: 'patch'
```

---

## Security Checks

To enable security scanning (Snyk), set the `enableSecurityChecks` parameter (Azure) or `ENABLE_SECURITY_CHECKS` env var (GitHub Actions):

### Azure Pipelines

```yaml
stages:
  - template: azure-pipelines/pipelines/python_pipeline.yml@templates
    parameters:
      enableSecurityChecks: true
      # ... other parameters
```

### GitHub Actions

Set the repository variable `ENABLE_SECURITY_CHECKS` to `true` in your repo settings, and provide the `SNYK_TOKEN` secret.
