# Agent: Add Stack

Add support for a new technology stack to the CI/CD template library.

## Steps

### 1. Azure Pipelines

1. **Pipeline** — `azure-pipelines/pipelines/{stack}_pipeline.yml`
   - Follow 5-stage pattern: Init → Build & Test → Security → Docker → Finalize
   - Parameterize everything (sonar, docker, git flow, mutation testing)

2. **Build & Test job** — `azure-pipelines/jobs/{stack}/{stack}_build_test.yml`
   - Language-specific: setup SDK, restore, build, test with coverage
   - SonarQube integration (conditional)

3. **Mutation test job** (optional) — `azure-pipelines/jobs/{stack}/{stack}_mutation_test.yml`

4. **Security checks** — `azure-pipelines/jobs/{stack}/security_checks.yml` (Snyk)

### 2. GitHub Actions (parity)

5. **Composite actions** — `github-actions/actions/{stack}/build-test/action.yml` + mutation-test + security-checks

6. **Workflow template** — `github-actions/workflow-templates/{stack}_pipeline.yml`

### 3. Finalization

7. **Update finalization** — Add language-specific version update in `finalisation.yml` (both Azure + GitHub)

8. **Documentation** — Update `docs/consumer-example.md` with usage example

### 4. Validation

9. **Lint** — `bash scripts/lint_yaml.sh`
10. **Validate** — `python3 scripts/validate_templates.py`

## Checklist
- [ ] Azure pipeline follows 5-stage pattern
- [ ] All parameters have `type` field
- [ ] No hardcoded IPs or org-specific values
- [ ] GitHub Actions parity complete
- [ ] Finalization handles language-specific version file
- [ ] YAML lint passes
- [ ] Template validation passes
- [ ] Consumer example documented
