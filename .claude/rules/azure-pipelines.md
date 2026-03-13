---
paths:
  - "azure-pipelines/**"
---

# Azure Pipelines Templates

## Template Hierarchy

```
pipelines/{stack}_pipeline.yml    → Entry point (consumed by other repos)
  └── jobs/{stack}/{task}.yml     → Language-specific job templates
       └── steps/{helper}.yml     → Reusable step templates
```

## Parameter Conventions

- Names: camelCase (`sonarProjectKey`, `containerRegistry`, `enableMutationTesting`)
- Every parameter MUST have a `type` field (enforced by `validate_templates.py`)
- Common parameters: `appName`, `jsonFile`, `versionIncrement`, `gitFlowType`, `sonarKey`, `dockerRegistry`, `containerRegistry`

## Path References

- **Pipelines → Jobs**: Absolute from repo root: `/jobs/dotnetcore/dotnetcore_build_test.yml`
- **Jobs → Steps**: Relative with backslashes: `..\..\steps\resolve_gitflow_context.yml`

## Conditional Execution

```yaml
# Skip on PRs
condition: ne(variables['Build.Reason'], 'PullRequest')

# Optional stages
${{ if eq(parameters.enableMutationTesting, true) }}:
```

## Variable Passing Between Stages

```yaml
# Set variable in step
echo "##vso[task.setvariable variable=DockerTag;isOutput=true]$VERSION"

# Read in dependent stage
variables:
  DockerTag: $[stageDependencies.Initialization.Versioning.outputs['version.DockerTag']]
```

## Anti-patterns

- Don't hardcode IPs, registry URLs, or org-specific values — always parameterize
- Don't forget `condition` on Docker/deploy/finalize stages (must skip on PR)
- Don't use absolute paths in job → step references (use relative)
- Don't forget `***NO_CI***` prefix in finalization commit (prevents infinite loops)
