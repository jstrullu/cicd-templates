# Portfolio Migration Map — source/Perso → cicd-templates

Concrete parameter mapping for each real consumer project in the org's
portfolio, built from reading every existing `azure-pipelines.yml` and
matching it against what the templates in this repo now support (as of the
CICD-6..16 audit, 2026-09-08).

**Prerequisite for every project below**: an Azure DevOps GitHub service
connection (`Project Settings → Service connections → New → GitHub`,
pointing at `jstrullu/cicd-templates`) must exist before the
`resources.repositories` block can resolve. Verified 2026-09-08: **none of
the 8 Azure DevOps projects below have any service connection configured**
(`az devops service-endpoint list` → empty on all of them). This is a
one-time manual step per project, not something this repo or an agent can
do without interactive Azure DevOps credentials — deliberately left out of
scope here and tracked as a manual action for later.

Every block below assumes that connection is named `github-connection` —
adjust to whatever name is actually used.

---

## Astro sites (SISOWebSite, AEAGestion, Agence de la Nive)

All three: `npm ci` → `astro check` → `astro build`, no unit tests, single
Docker image, `PUBLIC_GA_ID` build-arg, Helm deploy with `--set-string` for
secrets (SMTP creds). SISOWebSite/AEAGestion have `pr: none` — `git-sha`
versioning is the only sane fit (no PR to read a `#VERSION` override from).

### SISOWebSite

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
      appName: siso-distribution
      versioningStrategy: 'git-sha'
      typecheckScript: 'typecheck'
      buildScript: 'build'
      dockerPushMode: 'insecure-cli'
      dockerRegistry: '10.43.121.142:5000'
      dockerImageName: 'siso-distribution'
      insecureRegistryUrl: '10.43.121.142:5000'
      dockerBuildArgs: |
        PUBLIC_GA_ID=$(PUBLIC_GA_ID)
      deployMode: 'helm'
      helmChartPath: 'helm/siso-distribution'
      helmValuesFile: 'helm/siso-distribution/values-production.yaml'
      helmSetValues: |
        secrets.smtpUser=$(SMTP_USER)
        secrets.smtpPass=$(SMTP_PASS)
        env.PUBLIC_GA_ID=$(PUBLIC_GA_ID)
```

**Gap vs current pipeline**: none — this is a 1:1 replacement of the
existing CD stage.

### AEAGestion

Same shape as SISOWebSite, different names:

```yaml
    parameters:
      appName: aea-gestion
      versioningStrategy: 'git-sha'
      dockerPushMode: 'insecure-cli'
      dockerRegistry: '10.43.121.142:5000'
      dockerImageName: 'aea-gestion'
      insecureRegistryUrl: '10.43.121.142:5000'
      dockerBuildArgs: |
        PUBLIC_GA_ID=$(PUBLIC_GA_ID)
      deployMode: 'helm'
      helmChartPath: 'helm/aea-gestion'
      helmValuesFile: 'helm/aea-gestion/values-production.yaml'
      helmSetValues: |
        secrets.smtpUser=$(SMTP_USER)
        secrets.smtpPass=$(SMTP_PASS)
        env.PUBLIC_GA_ID=$(PUBLIC_GA_ID)
```

**Gap**: none — 1:1 replacement.

### Agence de la Nive

Has an extra `environment` parameter (staging/production) selecting a
values overlay file — not natively expressible as a single
`helmValuesFile` string. **Resolve it in the consumer pipeline** (compute
the file path there, pass the result down):

```yaml
parameters:
  - name: environment
    displayName: 'Environnement cible'
    type: string
    default: 'staging'
    values:
      - staging
      - production

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
      appName: agence-de-la-nive
      versioningStrategy: 'git-sha'
      dockerPushMode: 'insecure-cli'
      dockerRegistry: '10.43.121.142:5000'
      dockerImageName: 'agence-de-la-nive'
      insecureRegistryUrl: '10.43.121.142:5000'
      dockerBuildArgs: |
        PUBLIC_GA_ID=$(PUBLIC_GA_ID)
        PUBLIC_SITE_URL=$(PUBLIC_SITE_URL)
      deployMode: 'helm'
      helmChartPath: 'helm/agence-de-la-nive'
      # ${{ if eq(parameters.environment, 'staging') }} at compile time picks
      # the overlay; only one of the two branches ever exists in the
      # rendered pipeline, matching the original job's `$EXTRA_VALUES` logic.
      ${{ if eq(parameters.environment, 'staging') }}:
        helmValuesFile: 'helm/agence-de-la-nive/values-staging.yaml'
      ${{ if eq(parameters.environment, 'production') }}:
        helmValuesFile: 'helm/agence-de-la-nive/values-production.yaml'
      helmSetValues: |
        env.PUBLIC_GA_ID=$(PUBLIC_GA_ID)
        secrets.smtpUser=$(SMTP_USER)
        secrets.smtpPass=$(SMTP_PASS)
        secrets.contactToEmail=$(CONTACT_TO_EMAIL)
        secrets.postgresPassword=$(POSTGRES_PASSWORD)
        secrets.importToken=$(IMPORT_TOKEN)
        secrets.ipSalt=$(IP_SALT)
```

**Gap**: the original job passes secrets via `env:` on the step, specifically
to dodge a bash `$` -interpolation bug on values containing bcrypt hashes
(`admin:$2y$05$...`) — documented inline in the current pipeline as a real
incident. `helm_deploy.yml`'s `--set-string` loop reads `setValues` as
already-expanded pipeline variable text (same mechanism the working
pipeline uses via `$(SMTP_PASS)` substitution before the script runs, not
runtime env var expansion) — same class of risk exists here if a secret
ever contains literal `$`. **Verify with a real bcrypt-hash secret in this
project specifically before trusting it blindly** — not verified against
this exact edge case in the CICD-9/10 test harness (only alphanumeric test
secrets were used there).

---

## .NET projects — mono-image, no staging (paymenthub, mono only)

paymenthub is multi-image=false but staged — see the "staged deploy"
section below, it doesn't fit here.

*(no pure mono-image, non-staged .NET consumer exists in the audited
portfolio today — Belote is mobile/Play Store, out of scope for this repo
entirely, per the earlier CICD-6..16 audit decision)*

---

## .NET projects — multi-image (Portfolio, PentestSaaS, QualiForma)

### Portfolio (2 images: backend + frontend, frontend has 4 build-args)

```yaml
trigger:
  - master

pr:
  branches:
    include:
      - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/dotnetcore_pipeline.yml@templates
    parameters:
      appName: portfolio
      versioningStrategy: 'git-sha'
      projectFile: 'perso.tests/perso.tests.csproj'
      dockerPushMode: 'insecure-cli'
      dockerRegistry: '10.43.121.142:5000'
      insecureRegistryUrl: '10.43.121.142:5000'
      dockerImages:
        - name: backend
          dockerfile: perso.bff/Dockerfile
          context: .
        - name: frontend
          dockerfile: perso.front/Dockerfile
          context: perso.front/
          buildArgs: |
            VITE_API_BASE_URL=$(VITE_API_BASE_URL)
            VITE_API_KEY=$(VITE_API_KEY)
            VITE_ENTRA_TENANT_ID=a33b9b98-b9e6-45e8-be3c-e6e16243a4e8
            VITE_ENTRA_CLIENT_ID=186c4b3d-2c7c-4cb0-99d5-8486460f530e
      deployMode: 'helm'
      helmChartPath: 'helm/portfolio'
      helmValuesFile: 'helm/portfolio/values-production.yaml'
      helmSetValues: |
        secrets.postgresPassword=$(POSTGRES_PASSWORD)
        secrets.apiKey=$(API_KEY)
        secrets.githubToken=$(GITHUB_TOKEN)
        secrets.azureDevOpsToken=$(AZURE_DEVOPS_TOKEN)
        backend.config.entraTenantId=a33b9b98-b9e6-45e8-be3c-e6e16243a4e8
        backend.config.entraClientId=186c4b3d-2c7c-4cb0-99d5-8486460f530e
```

**Gaps**:
1. Image naming: the template names multi-images `{appName}-{item.name}`
   → `portfolio-backend` / `portfolio-frontend`. The current pipeline
   already uses exactly `portfolio-backend`/`portfolio-frontend` — matches,
   no change needed.
2. **No CI test/typecheck/lint step wired for the frontend job** in the
   template's `dotnetcore_build_test.yml` — the current pipeline runs
   `npm run typecheck`, `npm test`, `npm run build` on `perso.front/` as a
   *separate parallel job* (`Frontend`), which `dotnetcore_pipeline.yml`
   has no equivalent for (it's a single .NET-only `BuildAndTest` stage).
   **This is a real coverage gap, not solved by CICD-6..16** — migrating
   Portfolio as-is would silently drop frontend CI. Needs either a new
   parallel frontend-CI job parameter on `dotnetcore_pipeline.yml`, or
   accepting frontend CI runs elsewhere. Flagging rather than pretending
   the migration is complete.
3. `helm upgrade --wait` (current) vs `--atomic` (template) — the current
   pipeline deliberately uses `--wait` instead of `--atomic` so failed pods
   stay around for diagnostics, then does a manual `helm rollback` on
   failure. `helm_deploy.yml` uses `--atomic` (auto-rollback on failure,
   this repo's chosen default everywhere) — behavior change, not a bug,
   but the diagnostic step won't see failed-but-still-existing pods the
   same way Portfolio's current pipeline does. Worth confirming this
   tradeoff is acceptable before migrating.

### PentestSaaS (3 images: api + worker + frontend, separate Dockerfiles)

```yaml
trigger:
  branches:
    include:
      - master
      - feature/*
      - bugfix/*
      - hotfix/*
      - chore/*
pr:
  branches:
    include:
      - master

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/dotnetcore_pipeline.yml@templates
    parameters:
      appName: pentestsaas
      versioningStrategy: 'git-sha'
      projectFile: 'pentest-saas/PentestSaas.sln'
      dockerPushMode: 'insecure-cli'
      dockerRegistry: '10.43.121.142:5000'
      insecureRegistryUrl: '10.43.121.142:5000'
      dockerImages:
        - name: api
          dockerfile: pentest-saas/docker/Dockerfile.Api
          context: pentest-saas/
        - name: worker
          dockerfile: pentest-saas/docker/Dockerfile.Worker
          context: pentest-saas/
        - name: frontend
          dockerfile: pentest-saas-frontend/docker/Dockerfile.Frontend
          context: pentest-saas-frontend/
      deployMode: 'helm'
      helmChartPath: 'helm/pentestsaas'
      helmValuesFile: 'helm/pentestsaas/values-production.yaml'
      helmSetValues: |
        secrets.postgresPassword=$(POSTGRES_PASSWORD)
        secrets.rabbitmqPassword=$(RABBITMQ_PASSWORD)
        secrets.jwtSecret=$(JWT_SECRET)
```

**Gaps**:
1. Same frontend-CI-job gap as Portfolio (`pentest-saas-frontend/`'s
   `npm run lint`/`npm run build` job has no template equivalent).
2. Image naming: template produces `pentestsaas-api`/`pentestsaas-worker`/
   `pentestsaas-frontend` — matches current naming exactly.
3. Helm `--set api.image.tag=X --set worker.image.tag=X --set
   frontend.image.tag=X` (3 separate image tags) — `helm_deploy.yml`'s
   `imageTag` parameter only sets a single `--set image.tag=X`. **Not
   directly expressible** — would need 3 entries in `setValues` instead:
   `api.image.tag=$(BUILDID)` / `worker.image.tag=$(BUILDID)` /
   `frontend.image.tag=$(BUILDID)`, and leave `imageTag` empty. Doable, not
   shown above — add explicitly if migrating this project.
4. Pre-flight dependency health check (`kubectl rollout status
   statefulset/pentestsaas-postgresql`/`rabbitmq` before the Helm upgrade)
   has no template equivalent — would need a custom step inserted before
   or after the template stage, not currently parameterizable.

### QualiForma (2 images: api + frontend) — **not migratable as-is**

QualiForma has **no Helm chart**. Its deploy step is a raw
`kubectl apply -f deploy/k8s/qualiforma.yaml` followed by
`kubectl set image deployment/api ...` / `deployment/frontend ...`. Neither
`deployMode: 'helm'` (needs a chart) nor `deployMode: 'kube-manifest'`
(needs a Kubernetes-type Azure DevOps environment resource, which
`KubernetesManifest@0` requires and this project doesn't have configured)
reproduces this. **Migrating QualiForma's CI (build/test/EF-check) is
straightforward and uses the same dotnetcore_pipeline.yml parameters as
above for the Docker push side** — only the Deploy stage has no clean
template fit today. Two real options, neither done here:
1. Write a Helm chart for QualiForma (turns it into the same shape as
   Portfolio/PentestSaaS above), or
2. Extend `helm_deploy.yml`/create a `kubectl_apply_deploy.yml` job
   variant that does raw manifest apply + `kubectl set image` — not
   requested by any CICD ticket so far, would need a new ticket.

---

## .NET projects — staged Sandbox → Prod (paymenthub, ShopTemplate)

### paymenthub (mono-image)

```yaml
trigger:
  branches:
    include: [main, master, feature/*, bugfix/*, hotfix/*, chore/*]
pr:
  branches:
    include: [main, master]

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/dotnetcore_pipeline.yml@templates
    parameters:
      appName: paymenthub
      versioningStrategy: 'git-sha'
      projectFile: 'PaymentHub.slnx'
      dockerPushMode: 'insecure-cli'
      dockerRegistry: '10.43.121.142:5000'
      insecureRegistryUrl: '10.43.121.142:5000'
      deployMode: 'helm'
      enableStagedDeploy: true
      helmChartPath: 'helm/paymenthub'
      helmValuesFile: 'helm/paymenthub/values-production.yaml'
      helmSetValues: |
        secrets.postgresPassword=$(POSTGRES_PASSWORD)
        secrets.stripeApiKey=$(STRIPE_API_KEY)
        secrets.stripeWebhookSecret=$(STRIPE_WEBHOOK_SECRET)
        secrets.mollieApiKey=$(MOLLIE_API_KEY)
        secrets.authApiKeyHashSalt=$(AUTH_APIKEY_HASH_SALT)
      sandboxNamespace: 'paymenthub-sandbox'
      sandboxHelmValuesFile: 'helm/paymenthub/values-sandbox.yaml'
      sandboxHelmSetValues: |
        secrets.postgresPassword=$(SANDBOX_POSTGRES_PASSWORD)
      prodApprovalEnvironment: 'paymenthub-prod'
```

**Gap**: none structural — this is close to a 1:1 replacement. The trigger
branches (`main`/`master` mixed) need to stay on the consumer's own
`trigger:` block exactly as today (the template doesn't touch `trigger:`).

### ShopTemplate (2 images from 1 Dockerfile via `--target`, staged)

```yaml
trigger:
  branches:
    include: [main, master, feature/*, bugfix/*, hotfix/*, chore/*]
pr:
  branches:
    include: [main, master]

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

stages:
  - template: azure-pipelines/pipelines/dotnetcore_pipeline.yml@templates
    parameters:
      appName: shoptemplate
      versioningStrategy: 'git-sha'
      projectFile: 'backend/ShopTemplate.slnx'
      dockerPushMode: 'insecure-cli'
      dockerRegistry: '10.43.121.142:5000'
      insecureRegistryUrl: '10.43.121.142:5000'
      dockerImages:
        - name: api
          dockerfile: Dockerfile
          target: api
        - name: frontend
          dockerfile: Dockerfile
          target: frontend
          buildArgs: |
            BRAND=$(BRAND)
            VITE_API_URL=$(SANDBOX_API_URL)
      deployMode: 'helm'
      enableStagedDeploy: true
      helmChartPath: 'helm/shoptemplate'
      helmValuesFile: 'helm/shoptemplate/values-production.yaml'
      helmSetValues: |
        secrets.postgresPassword=$(POSTGRES_PASSWORD)
        secrets.paymentHubApiKey=$(PAYMENTHUB_API_KEY)
        secrets.paymentHubHmacSecret=$(PAYMENTHUB_HMAC_SECRET)
      sandboxHelmValuesFile: 'helm/shoptemplate/values-sandbox.yaml'
      sandboxHelmSetValues: |
        secrets.postgresPassword=$(SANDBOX_POSTGRES_PASSWORD)
        secrets.paymentHubApiKey=$(SANDBOX_PAYMENTHUB_API_KEY)
        secrets.paymentHubHmacSecret=$(SANDBOX_PAYMENTHUB_HMAC_SECRET)
      prodApprovalEnvironment: 'shoptemplate-prod'
```

**Gaps**:
1. Frontend needs a **different `VITE_API_URL` build-arg between sandbox
   and prod** (`$(SANDBOX_API_URL)` vs `$(PROD_API_URL)`, baked in at build
   time, not at deploy time). `dockerImages[].buildArgs` is a single value
   passed once to the whole staged flow (both sandbox and prod stages reuse
   the *same* built image per CICD-13's design — same tag promoted, not
   rebuilt). ShopTemplate's actual pipeline **rebuilds the frontend image
   twice** (once per environment, two different tags: `sandbox-X` and
   `prod-X`) specifically because the API URL is baked in — this
   contradicts the "same image promoted, not rebuilt" assumption
   `enableStagedDeploy` was built on. **This is a real design mismatch, not
   a small gap** — CICD-13 was scoped to paymenthub's shape (single image,
   truly promoted unchanged); ShopTemplate's frontend needs a rebuild per
   environment. Migrating ShopTemplate's frontend stage as designed above
   would deploy the sandbox `VITE_API_URL` to production too. **Do not
   migrate ShopTemplate's frontend to the current `enableStagedDeploy`
   without a follow-up ticket** to support per-stage build-args, or keep
   ShopTemplate's frontend build as a bespoke step outside the template.
2. Frontend needs a `${{ if eq(parameters.environment, ...) }}`-computed
   secrets set. `frontend.image.tag` uses `sandbox-$(IMAGE_TAG)`/
   `prod-$(IMAGE_TAG)` prefixes in the original — `helm_deploy.yml`'s
   `imageTag` parameter sets a single unprefixed tag on `image.tag`, not
   per-component prefixed tags — same limitation as PentestSaaS's #3 above.

### ShopTemplate — deploy: `enableStagedDeploy` + `preDeployDockerBuilds` (CICD-17)

`enableStagedDeploy` (CICD-13) assumed the same image, built once,
promoted unchanged from sandbox to prod. ShopTemplate's frontend breaks
that assumption: `VITE_API_URL` is baked in at build time, so it must be
**rebuilt** with a different value for sandbox vs prod — not the design
`helm_deploy.yml`/`helm_deploy_gated.yml` supported until now.

**Fix**: `preDeployDockerBuilds` on both jobs — an optional list of images
to build/push right before the Helm upgrade, each with its own full tag
(no shared `imageTag` reuse). Wired into `dotnetcore_pipeline.yml` as
`sandboxPreDeployDockerBuilds`/`prodPreDeployDockerBuilds` (both `helm`
mode only, empty by default — every other consumer of `enableStagedDeploy`,
i.e. paymenthub, is completely unaffected).

The API image (unchanged across environments) is still built once in
`Docker_Build_And_Publish` via the existing multi-image job (CICD-12) and
promoted via `imageTag` — only the frontend needs `preDeployDockerBuilds`.

```yaml
trigger:
  branches:
    include: [main, master, feature/*, bugfix/*, hotfix/*, chore/*]
pr:
  branches:
    include: [main, master]

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

extends:
  template: /azure-pipelines/pipelines/dotnetcore_pipeline.yml@templates
  parameters:
    appName: shoptemplate
    gitFlowType: trunk-based
    versioningStrategy: git-sha
    projectFile: backend/ShopTemplate.slnx
    dockerPushMode: insecure-cli
    insecureRegistryUrl: registry.internal:5000
    dockerRegistry: registry.internal:5000
    # API image only — same SHA promoted sandbox -> prod, no rebuild needed.
    dockerImages:
      - name: api
        dockerfile: Dockerfile
        target: api
    deployMode: helm
    helmChartPath: helm/shoptemplate
    enableStagedDeploy: true
    sandboxNamespace: shoptemplate-sandbox
    sandboxHelmValuesFile: helm/shoptemplate/values-sandbox.yaml
    sandboxHelmSetValues: |
      secrets.postgresPassword=$(SANDBOX_POSTGRES_PASSWORD)
      secrets.paymentHubApiKey=$(SANDBOX_PAYMENTHUB_API_KEY)
      secrets.paymentHubHmacSecret=$(SANDBOX_PAYMENTHUB_HMAC_SECRET)
      frontend.image.tag=sandbox-$(BUILDID)
    sandboxPreDeployDockerBuilds:
      - name: shoptemplate-frontend
        target: frontend
        tag: sandbox-$(BUILDID)
        alsoTag: sandbox-latest
        buildArgs: |
          BRAND=$(BRAND)
          VITE_API_URL=$(SANDBOX_API_URL)
    helmValuesFile: helm/shoptemplate/values-production.yaml
    helmSetValues: |
      secrets.postgresPassword=$(POSTGRES_PASSWORD)
      secrets.paymentHubApiKey=$(PAYMENTHUB_API_KEY)
      secrets.paymentHubHmacSecret=$(PAYMENTHUB_HMAC_SECRET)
      frontend.image.tag=prod-$(BUILDID)
    prodApprovalEnvironment: shoptemplate-prod
    prodPreDeployDockerBuilds:
      - name: shoptemplate-frontend
        target: frontend
        tag: prod-$(BUILDID)
        alsoTag: prod-latest
        buildArgs: |
          BRAND=$(BRAND)
          VITE_API_URL=$(PROD_API_URL)
```

One gap this does **not** close: the original's separate `Backend`/
`Frontend` CI jobs (dotnet test + npm lint/test/build on every PR) — same
"frontend CI has no template slot" limitation already flagged for
Portfolio/PentestSaaS above. `BuildAndTest` in `dotnetcore_build_test.yml`
only runs the .NET side; ShopTemplate's `npm run lint`/`npm test` would be
dropped if migrated as shown. Not in scope for CICD-17 (tracked as the
same open gap as Portfolio/PentestSaaS, no ticket yet — low urgency, easy
to keep as a bespoke extra CI job outside the template if needed).

**Real verification done**: `validate_templates.py` 50/50, parameter
cross-check (job params match every pipeline call-site) done
programmatically, the `docker build`/`docker push` command construction
was extracted and run against a mock `docker()` with ShopTemplate's exact
real values (frontend, `--target frontend`, two build-args, two tags) —
output flags match the original pipeline's real `docker build` command
1:1. **Not yet verified**: an actual pipeline run against ShopTemplate's
real cluster/Helm chart.

---

## RestoTemplate (multi-client monorepo, CICD-20)

Original pipeline: `client` parameter selects `clients/<slug>` to build and
`helm/values/<slug>.yaml` to deploy; secrets come from a per-client
`Resto-<slug>` variable group; release/namespace is `resto-<slug>`.

Two real gaps, both closed by this ticket:
1. `CLIENT=$(CLIENT)` was exported before every `npm run typecheck`/`npm run
   build` call — no existing parameter threaded arbitrary env vars into the
   Astro build job. Added `buildEnvVars` (multi-line `KEY=VALUE`, parsed the
   same way `dockerBuildArgs`/`helmSetValues` already are) to both
   `astro_pipeline.yml` and `jobs/astro/astro_build_test.yml`.
2. The `Resto-<slug>` variable group was linked directly in the consumer
   pipeline's `CD` stage `variables:` block — no template parameter existed
   to link an arbitrary variable group into the `Deploy` stage. Added
   `deployVariableGroup` (empty by default = unchanged behavior for every
   other consumer).

```yaml
trigger:
  branches:
    include: [master]
pr: none

parameters:
  - name: client
    type: string
    default: 'demo-woods'

resources:
  repositories:
    - repository: templates
      type: github
      name: jstrullu/cicd-templates
      endpoint: github-connection

extends:
  template: /azure-pipelines/pipelines/astro_pipeline.yml@templates
  parameters:
    appName: resto-${{ parameters.client }}
    gitFlowType: trunk-based
    versioningStrategy: git-sha
    nodeVersion: '20.x'
    packageManager: npm
    typecheckScript: typecheck
    buildScript: build
    buildEnvVars: CLIENT=${{ parameters.client }}
    dockerPushMode: insecure-cli
    dockerImageName: resto-${{ parameters.client }}
    insecureRegistryUrl: registry.internal:5000
    deployMode: helm
    helmChartPath: helm/resto-site
    helmValuesFile: helm/values/${{ parameters.client }}.yaml
    deployVariableGroup: Resto-${{ parameters.client }}
    helmSetValues: |
      secrets.smtpUser=$(SMTP_USER)
      secrets.smtpPass=$(SMTP_PASS)
```

Two things this block deliberately does **not** attempt to reproduce:
- The original's conditional `BASIC_AUTH_ARGS` (only set `--set-string
  ingress.basicAuth.htpasswd=...` when the client has that secret defined).
  `helmSetValues` is static text here — a client without
  `BASIC_AUTH_HTPASSWD` in its variable group would pass an empty value.
  Verify whether `helm_deploy.yml`'s `--set-string` with an empty RHS is a
  no-op or sets an empty string before relying on this for a client that
  needs the distinction.
- `deploy: false` as a manual on/off switch for the CD stage — replaced by
  `gitflow.shouldDeploy` (trunk-based: deploys every push to `master`),
  which changes the trigger semantics slightly (no more per-run opt-out).
  Acceptable trade-off if manual control isn't needed; otherwise a
  `disableDeploy`-style override would need a small template change.

**Real verification done**: `buildEnvVars`/`deployVariableGroup` YAML
validates (`validate_templates.py`, 50/50), the bash env-var parsing logic
was extracted and run standalone with the exact `CLIENT=demo-woods` value
this project uses (single-line and multi-line-with-blank-line cases both
resolved correctly). **Not yet verified**: an actual pipeline run against
RestoTemplate's real Helm chart/cluster — do that before considering the
migration complete, per the two caveats above.

---

## Summary

| Project | Stack template | Ready to migrate as shown? | Real gap found |
|---|---|---|---|
| SISOWebSite | astro | ✅ yes | none |
| AEAGestion | astro | ✅ yes | none |
| Agence de la Nive | astro | ✅ yes, with consumer-side `${{ if }}` for the values overlay | secret-with-`$`-character risk not test-covered |
| Portfolio | dotnetcore | ⚠️ Docker/deploy yes, **frontend CI job has no template slot** | frontend CI dropped if migrated as-is |
| PentestSaaS | dotnetcore | ⚠️ same as Portfolio + pre-flight dependency check has no slot | **on standby (user decision 2026-09-08)** — frontend CI dropped; dependency pre-flight dropped; per-image tag needs manual `setValues` workaround |
| QualiForma | dotnetcore | ❌ no | **on standby (user decision 2026-09-08)** — CICD-18: no Helm chart exists, Deploy stage not migratable without either writing one or a new job variant |
| paymenthub | dotnetcore, staged | ✅ yes | none |
| ShopTemplate | dotnetcore, staged | ✅ yes — CICD-17 delivered | frontend CI (npm lint/test) has no template slot, same as Portfolio/PentestSaaS above |

**3 of 8 are ready to paste in today** (after the manual service connection
step). **1 needs a documented gap accepted** (Portfolio). **2 are on
standby by user decision, not blockers** (PentestSaaS, QualiForma — the
technical analysis below still stands for whenever standby lifts).
**ShopTemplate is now migratable** (CICD-17 delivered `preDeployDockerBuilds`
— same frontend-CI gap as Portfolio/PentestSaaS, but the deploy blocker is
resolved). Agence de la Nive is covered separately above (not part of this
multi-image group).

---

## The rest of the Azure DevOps portfolio (14 projects total)

The 8 above cover every project that already fits one of the 9 existing
stacks. The remaining Azure DevOps projects, checked 2026-09-08:

| Project | Verdict | Why |
|---|---|---|
| **Belote** | ❌ blocked — CICD-19 | Mobile Android + signed APK/AAB + Play Store publish via fastlane. No stack covers this (Flutter deploys to Firebase, not Play Store). |
| **sc-app** | ❌ blocked — CICD-19 | Same mobile/Play Store gap as Belote, plus a pinned .NET 9 SDK (global.json) distinct from the root SDK 10 — needs its own parameter. Backend/API portion (`.NET` + Helm) already fits `dotnetcore_pipeline.yml` as-is; only the mobile job is blocked. |
| **RestoTemplate** | ✅ migratable — CICD-20 delivered | Multi-client monorepo. `astro_pipeline.yml` now supports it via `buildEnvVars` (injects `CLIENT=<slug>` before typecheck/build) and `deployVariableGroup` (links the per-client `Resto-<slug>` variable group into the Deploy stage). See full block below. |
| **Infrastructure** | ❌ out of scope, not a migration candidate | Pure infra-as-code (Helm/kubectl only, no application to build/test, no Docker image, `git diff`-based change detection driving per-component conditional stages, manual-approval gates on cluster-critical components). This is a fundamentally different pipeline shape than "build → test → push → deploy one app" — cicd-templates was never designed for it and extending it to fit would dilute what the 9 stacks actually do well. Not tracked as a CICD ticket; keep Infrastructure's bespoke pipeline as-is. |
| **PentestSaaS** | 🟡 on standby | User decision 2026-09-08: put aside for now, alongside QualiForma. Build/test/Docker fits `dotnetcore_pipeline.yml` as-is; deploy fits `deployMode: helm`. Only real gap was a CI frontend job with no template equivalent — not a blocker, revisit when standby lifts. |
| **QualiForma** | 🟡 on standby — CICD-18 | User decision 2026-09-08: put aside for now, alongside PentestSaaS. CICD-18 still tracks the real technical gap (no Helm chart) for when standby lifts, downgraded to Low priority, labeled `en-standby`. |
| **Kuenta** | Deliberately excluded | 3 years inactive (last CI run 2023-09-12) — user decision 2026-09-08, not tracked. |
| **CommandAppli** | Deliberately excluded | No pipeline configured, not cloned locally — user decision 2026-09-08, not tracked. |

**Updated totals**: of the 14 Azure DevOps projects in the org, **11 are
realistically in scope for cicd-templates** (8 mapped above + Belote +
sc-app + RestoTemplate pending CICD-19/20), **2 are on standby by user
decision** (PentestSaaS, QualiForma — CICD-18 downgraded to Low), **1 is
intentionally out of scope by design** (Infrastructure), **2 are excluded
by explicit user decision** (Kuenta, CommandAppli).
