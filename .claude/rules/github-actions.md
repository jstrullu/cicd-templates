---
paths:
  - "github-actions/**"
---

# GitHub Actions Templates

## Structure

```
actions/{stack}/{task}/action.yml    → Composite actions (building blocks)
workflow-templates/{stack}_pipeline.yml  → Full pipelines (copied into consumer)
```

## Composite Action Pattern

```yaml
name: 'Build & Test (.NET)'
description: 'Build and test .NET Core project'
inputs:
  sonar-project-key:    # kebab-case inputs
    description: 'SonarQube project key'
    required: false
runs:
  using: 'composite'
  steps:
    - name: Setup .NET
      uses: actions/setup-dotnet@v4
      with:
        dotnet-version: '10.0.x'
```

## Input Naming

kebab-case for all inputs: `sonar-project-key`, `container-registry`, `enable-mutation-testing`.
(Azure uses camelCase — this is a platform convention difference.)

## Workflow Template Usage

Consumer copies template into `.github/workflows/` and configures secrets:
```yaml
uses: jstrullu/cicd/github-actions/actions/dotnetcore/build-test@master
with:
  sonar-project-key: ${{ secrets.SONAR_PROJECT_KEY }}
```

## Secrets Convention

- `SONAR_TOKEN`, `SONAR_HOST_URL` — SonarQube
- `SNYK_TOKEN` — Security checks
- GitHub token available via `${{ github.token }}`

## Parity with Azure

Every Azure pipeline has a GitHub Actions equivalent. When modifying one, update the other.
Same stages, same logic, same parameters (adapted to platform conventions).
