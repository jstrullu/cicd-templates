# Contributing

Thank you for your interest in contributing to this CI/CD pipeline templates project! This guide will help you get started.

## How to Contribute

### Reporting Issues

- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) for pipeline errors or unexpected behavior
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) for new pipeline templates, steps, or improvements
- Search existing issues before creating a new one to avoid duplicates

### Submitting Changes

1. **Fork** the repository
2. **Create a branch** from `main` for your changes
3. **Make your changes** following the guidelines below
4. **Test your templates** against a real Azure DevOps project if possible
5. **Submit a pull request** using the PR template

### Development Guidelines

#### Pipeline Template Structure

Follow the existing directory layout:

```
azure-pipelines/
├── pipelines/    # Entry-point pipeline definitions
├── jobs/         # Reusable job templates (organized by language)
└── steps/        # Reusable step templates
```

#### Naming Conventions

- Use `snake_case` for file names (e.g., `docker_build_and_publish.yml`)
- Use descriptive names that reflect the template's purpose
- Group language-specific templates in subdirectories under `jobs/`

#### Template Parameters

- Always define a `type` for each parameter
- Provide sensible `default` values when possible
- Use `displayName` for parameters visible in the Azure DevOps UI
- Parameterize service connection names — never hardcode organization-specific values

#### Version Compatibility

- Templates should work with the latest Azure DevOps agent images
- Document any required Azure DevOps extensions in the template comments
- When adding a `gitFlowType`-aware template, ensure all four strategies are handled

#### Commit Messages

- Use clear, descriptive commit messages
- Start with a verb in imperative mood (e.g., "Add", "Fix", "Update")
- Reference related issues when applicable (e.g., "Fix #42")

### What We're Looking For

- New language/framework pipeline templates
- Improvements to existing templates (better defaults, more parameters)
- Bug fixes for edge cases in versioning or deployment logic
- Documentation improvements
- GitHub Actions equivalents of existing Azure Pipelines templates

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.
