---
name: Bug Report
about: Report a problem with a pipeline template
title: '[Bug] '
labels: bug
assignees: ''
---

## Template affected

Which pipeline template or step file is affected?

- [ ] `dotnetcore_pipeline.yml`
- [ ] `java_gradle_pipeline.yml`
- [ ] `java_gradle_avro_pipeline.yml`
- [ ] `angular_npm_pipeline.yml`
- [ ] `flutter_pipeline.yml`
- [ ] `json_semantic_version.yml`
- [ ] `resolve_gitflow_context.yml`
- [ ] `finalisation.yml`
- [ ] `docker_build_and_publish.yml`
- [ ] `kube_deploy.yml`
- [ ] Other: <!-- specify -->

## Description

A clear description of the bug.

## Pipeline configuration

```yaml
# Paste your pipeline parameters or the relevant part of your azure-pipelines.yml
```

## Expected behavior

What you expected to happen.

## Actual behavior

What actually happened. Include pipeline logs if possible.

## Environment

- Azure DevOps agent image: <!-- e.g., ubuntu-latest -->
- Git flow type: <!-- e.g., gitflow, github-flow -->
- Branch: <!-- e.g., develop, release/1.0 -->
- Build reason: <!-- e.g., IndividualCI, PullRequest -->
