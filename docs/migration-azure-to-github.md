# Migration Guide: Azure Pipelines to GitHub Actions

Step-by-step guide for migrating from Azure Pipelines templates to GitHub Actions workflow templates.

---

## Key Differences

| Concept | Azure Pipelines | GitHub Actions |
|---------|----------------|----------------|
| Pipeline file | `azure-pipelines.yml` | `.github/workflows/*.yml` |
| Template system | `template:` references (stages/jobs/steps) | Composite actions (`uses:`) |
| Multi-stage | Stages with `dependsOn` | Jobs with `needs` |
| Conditions | `condition: eq(...)` expressions | `if:` expressions |
| Variables | `variables:` + `parameters:` | `env:` + `inputs:` |
| Service connections | Named connections in project settings | Repository secrets |
| Artifacts | `PublishPipelineArtifact` / `DownloadPipelineArtifact` | `actions/upload-artifact` / `actions/download-artifact` |
| PR detection | `ne(variables['Build.Reason'], 'PullRequest')` | `github.event_name != 'pull_request'` |
| Skip CI | `***NO_CI***` in commit message | `[skip ci]` in commit message |

---

## Migration Checklist

### 1. Create version file

Both platforms use the same `cicd.json` file. No change needed if already present.

### 2. Copy the workflow template

1. Find your stack's workflow template in `github-actions/workflow-templates/`
2. Copy it to `.github/workflows/pipeline.yml` in your consumer repo
3. Edit the `env:` section with your project's values

### 3. Map parameters to env vars

| Azure Parameter | GitHub Actions env var | Notes |
|----------------|----------------------|-------|
| `versionIncrement` | `VERSION_INCREMENT` | Same values: `patch`, `minor`, `major` |
| `jsonFile` | `FICHIER_JSON` | Default: `cicd.json` |
| `sonarKey` | `SONAR_KEY` | SonarQube project key |
| `javaVersion` | `JAVA_VERSION` | e.g., `17` |
| `goVersion` | `GO_VERSION` | e.g., `1.22` |
| `pythonVersion` | `PYTHON_VERSION` | e.g., `3.12` |
| `nodeVersion` | `NODE_VERSION` | e.g., `20` |
| `dockerRegistry` | `DOCKER_REGISTRY` | e.g., `ghcr.io/org` |
| `containerRegistry` | *(see secrets below)* | Replaced by username/password secrets |
| `appName` / kube namespace | `KUBE_NAMESPACE` | Kubernetes namespace |
| `gitFlowType` | *(not yet ported)* | GitHub Actions uses github-flow by default |
| `projectFile` | `PROJECT_FILE` | .NET `.csproj` path |
| `pomFile` | `POM_FILE` | Maven POM path |
| `requirementsFile` | `REQUIREMENTS_FILE` | Python requirements path |
| `packageManager` | `PACKAGE_MANAGER` | `npm` or `yarn` |

### 4. Map service connections to secrets

| Azure Service Connection | GitHub Secret(s) | How to set |
|--------------------------|------------------|------------|
| SonarQube (`sonarConnection`) | `SONAR_HOST_URL` + `SONAR_TOKEN` | Settings > Secrets and variables > Actions |
| Docker registry (`containerRegistry`) | `DOCKER_USERNAME` + `DOCKER_PASSWORD` | Use access tokens, not passwords |
| Kubernetes | `KUBECONFIG` | Base64-encoded kubeconfig file |
| Snyk (`snykConnection`) | `SNYK_TOKEN` | Snyk API token |

### 5. Configure permissions

Add to your workflow file if using finalisation (git push):

```yaml
permissions:
  contents: write
  pull-requests: read
```

### 6. Enable security checks (optional)

1. Go to **Settings > Secrets and variables > Actions > Variables**
2. Create `ENABLE_SECURITY_CHECKS` with value `true`
3. Add the `SNYK_TOKEN` secret

### 7. Remove Azure Pipelines config

Once the GitHub Actions workflow is working:
1. Delete `azure-pipelines.yml` from your repo
2. Remove the pipeline definition from Azure DevOps
3. Remove any Azure DevOps badges from your README

---

## Per-Stack Migration Notes

### .NET Core

Azure:
```yaml
stages:
  - template: azure-pipelines/pipelines/dotnetcore_pipeline.yml@templates
    parameters:
      sonarKey: 'my-project'
      projectFile: 'src/MyApp/MyApp.csproj'
      securityTargetDir: 'src/MyApp'
```

GitHub Actions: Copy `github-actions/workflow-templates/dotnetcore_pipeline.yml` and set:
```yaml
env:
  SONAR_KEY: 'my-project'
  PROJECT_FILE: 'src/MyApp/MyApp.csproj'
  SECURITY_TARGET_FILE: 'MyApp.sln'
```

### Java/Gradle

Azure:
```yaml
stages:
  - template: azure-pipelines/pipelines/java_gradle_pipeline.yml@templates
    parameters:
      sonarKey: 'my-project'
      javaVersion: '17'
      dockerRegistry: 'myapp'
      containerRegistry: 'my-connection'
```

GitHub Actions: Copy `github-actions/workflow-templates/java_gradle_pipeline.yml` and set:
```yaml
env:
  SONAR_KEY: 'my-project'
  JAVA_VERSION: '17'
  DOCKER_REGISTRY: 'ghcr.io/my-org'
```

### Java/Maven

Azure:
```yaml
stages:
  - template: azure-pipelines/pipelines/java_maven_pipeline.yml@templates
    parameters:
      sonarKey: 'my-project'
      javaVersion: '17'
      pomFile: 'pom.xml'
```

GitHub Actions: Copy `github-actions/workflow-templates/java_maven_pipeline.yml` and set:
```yaml
env:
  SONAR_KEY: 'my-project'
  JAVA_VERSION: '17'
  POM_FILE: 'pom.xml'
```

### Go

Azure:
```yaml
stages:
  - template: azure-pipelines/pipelines/go_pipeline.yml@templates
    parameters:
      sonarKey: 'my-project'
      goVersion: '1.22'
```

GitHub Actions: Copy `github-actions/workflow-templates/go_pipeline.yml` and set:
```yaml
env:
  SONAR_KEY: 'my-project'
  GO_VERSION: '1.22'
```

### Node.js/TypeScript

Azure:
```yaml
stages:
  - template: azure-pipelines/pipelines/node_pipeline.yml@templates
    parameters:
      sonarKey: 'my-project'
      nodeVersion: '20.x'
      packageManager: 'npm'
```

GitHub Actions: Copy `github-actions/workflow-templates/node_pipeline.yml` and set:
```yaml
env:
  SONAR_KEY: 'my-project'
  NODE_VERSION: '20'
  PACKAGE_MANAGER: 'npm'
```

### Python

Azure:
```yaml
stages:
  - template: azure-pipelines/pipelines/python_pipeline.yml@templates
    parameters:
      sonarKey: 'my-project'
      pythonVersion: '3.12'
      requirementsFile: 'requirements.txt'
```

GitHub Actions: Copy `github-actions/workflow-templates/python_pipeline.yml` and set:
```yaml
env:
  SONAR_KEY: 'my-project'
  PYTHON_VERSION: '3.12'
  REQUIREMENTS_FILE: 'requirements.txt'
```

### Angular

Azure:
```yaml
stages:
  - template: azure-pipelines/pipelines/angular_npm_pipeline.yml@templates
    parameters:
      sonarKey: 'my-project'
```

GitHub Actions: Copy `github-actions/workflow-templates/angular_pipeline.yml` and set:
```yaml
env:
  SONAR_KEY: 'my-project'
```

### Flutter

Azure:
```yaml
stages:
  - template: azure-pipelines/pipelines/flutter_pipeline.yml@templates
```

GitHub Actions: Copy `github-actions/workflow-templates/flutter_pipeline.yml` — Flutter uses a different versioning system (Cider/pubspec.yaml) so the workflow structure is unique.

---

## Conditions Syntax Reference

| Azure Pipelines | GitHub Actions |
|----------------|----------------|
| `eq(variables['Build.Reason'], 'PullRequest')` | `github.event_name == 'pull_request'` |
| `ne(variables['Build.Reason'], 'PullRequest')` | `github.event_name != 'pull_request'` |
| `eq(variables['Build.SourceBranch'], 'refs/heads/master')` | `github.ref == 'refs/heads/master'` |
| `succeeded()` | `success()` |
| `failed()` | `failure()` |
| `always()` | `always()` |
| `and(cond1, cond2)` | `cond1 && cond2` |
| `or(cond1, cond2)` | `cond1 \|\| cond2` |
