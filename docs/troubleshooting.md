# Troubleshooting Guide

Common issues when using the CI/CD templates and how to resolve them.

---

## Version Bump Not Working

### PR title format not recognized

The version bump override expects the format `#VERSION <level>` in the PR title (case-insensitive).

**Valid:**
- `feat: add feature #VERSION minor`
- `fix: patch bug #VERSION PATCH`
- `feat!: breaking change #VERSION major`

**Invalid:**
- `feat: add feature #version` (missing level)
- `feat: add feature VERSION minor` (missing `#`)

### Missing cicd.json

The initialization stage reads `cicd.json` from the consumer repo root. If the file doesn't exist, the pipeline creates it automatically with `{"version":"0.0.0"}`. However, if you see errors about missing files:

1. Verify `cicd.json` exists at the repo root
2. Check the `jsonFile` parameter matches the actual file path
3. Ensure the file contains valid JSON: `{"version":"0.0.0"}`

### Version not incrementing on develop/release branches (gitflow)

In gitflow mode, `main`/`master` does **not** bump — it inherits the version from the merged branch. Check that:
- `gitFlowType` is set to `gitflow`
- `developIncrement`, `releaseIncrement`, `hotfixIncrement` are set as desired
- You're merging from the correct branch

---

## SonarQube Issues

### Missing SonarQube project key

Set the `sonarKey` parameter (Azure) or `SONAR_KEY` env var (GitHub Actions). An empty value skips SonarQube analysis entirely.

### SonarQube tasks commented out (Angular/Flutter)

Some Angular and Flutter Sonar steps are currently commented out in the build templates. To enable them:
1. Uncomment the relevant steps in the build-test action/job
2. Provide the correct `sonarKey` and SonarQube credentials

### SonarQube connection failure

**Azure Pipelines:** Verify the `sonarConnection` service connection exists in your Azure DevOps project (default: `Sonar`).

**GitHub Actions:** Ensure the following secrets are set:
- `SONAR_HOST_URL` — URL of your SonarQube server
- `SONAR_TOKEN` — Authentication token

---

## Service Connection Errors (Azure DevOps)

### "Service connection not found"

Azure DevOps service connections must be configured at the project level:

| Connection | Parameter | Default | Purpose |
|------------|-----------|---------|---------|
| SonarQube | `sonarConnection` | `Sonar` | Code quality analysis |
| Docker registry | `containerRegistry` | *(required)* | Container image push |
| Git repos | `reposConnection` | `Repos` | PR title parsing via API |
| Snyk | `snykConnection` | `Snyk Security` | Security scanning |

Verify that:
1. The connection exists in **Project Settings > Service connections**
2. The pipeline has permission to use the connection
3. The connection name matches the parameter value

---

## Docker Authentication Failures

### Registry login failed

**Azure Pipelines:**
- Verify the `containerRegistry` service connection is configured and authorized
- Check that the service principal/credentials haven't expired

**GitHub Actions:**
- Ensure `DOCKER_USERNAME` and `DOCKER_PASSWORD` secrets are set
- For GitHub Container Registry (ghcr.io), use a personal access token with `write:packages` scope
- For Docker Hub, use an access token (not your password)

### Image push rejected

- Check that the `dockerRegistry` value matches the repository path in your registry
- Verify your account/organization has storage capacity

---

## Kubernetes Deployment Issues

### Token replacement not working

The `kube_deploy` job replaces tokens in manifest files from `.kube/`. Ensure:
1. Your manifests are in the `.kube/` directory at the repo root
2. Tokens use the correct format: `#{VARIABLE_NAME}#` (Azure) or `${VARIABLE_NAME}` (GitHub Actions)
3. The `BUILDID` variable is available (it's set from the initialization stage output)

### Manifest paths not found

- Check that `.kube/` directory exists and contains your YAML manifests
- File names must end with `.yml` or `.yaml`

### Namespace doesn't exist

The templates don't create namespaces automatically. Pre-create the namespace:
```bash
kubectl create namespace <your-namespace>
```

---

## Git Push Failures in Finalisation

### "Permission denied" or "403"

**Azure Pipelines:**
- The pipeline needs `persistCredentials: true` on checkout (already set in templates)
- The build service account needs **Contribute** permission on the repository
- For protected branches, grant **Bypass policies** to the build service identity

**GitHub Actions:**
- The default `GITHUB_TOKEN` must have `contents: write` permission
- Add to your workflow:
  ```yaml
  permissions:
    contents: write
  ```
- For protected branches, use a personal access token or GitHub App token instead of `GITHUB_TOKEN`

### "Branch is protected"

The finalisation stage commits and pushes to the current branch. If it's protected:
- **Azure DevOps:** Allow the build service to bypass branch policies
- **GitHub:** Add a branch protection bypass rule for your CI bot, or use a token with admin privileges

### Merge conflicts on push

This can happen if another commit was pushed between the build start and finalisation. The templates use `git push origin HEAD` which will fail on conflicts. Re-run the pipeline to resolve.

---

## GitHub Actions: GITHUB_TOKEN Permissions

### "Resource not accessible by integration"

The default `GITHUB_TOKEN` has limited permissions. Add these permissions to your workflow:

```yaml
permissions:
  contents: write      # For git push in finalisation
  pull-requests: read  # For PR title detection
  packages: write      # For GHCR (if using GitHub Container Registry)
```

### Actions from external repos blocked

If your organization restricts GitHub Actions:
1. Go to **Settings > Actions > General**
2. Under "Actions permissions", allow actions from `jstrullu/cicd`
3. Or use the "Allow select actions" option and add `jstrullu/cicd/*`

---

## Security Checks (Snyk)

### Snyk authentication failed

**Azure Pipelines:** Verify the `snykConnection` service connection (default: `Snyk Security`).

**GitHub Actions:** Ensure the `SNYK_TOKEN` secret is set with a valid Snyk API token.

### Security checks not running

Security checks are opt-in:
- **Azure Pipelines:** Set `enableSecurityChecks: true` in your pipeline parameters
- **GitHub Actions:** Set the repository variable `ENABLE_SECURITY_CHECKS` to `true`
