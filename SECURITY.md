# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in these pipeline templates, please report it responsibly.

**Do not open a public issue for security vulnerabilities.**

Instead, please report vulnerabilities by emailing the maintainers or by using GitHub's private vulnerability reporting feature on this repository.

### What to include

- Description of the vulnerability
- Which template file(s) are affected
- Steps to reproduce or proof of concept
- Potential impact (e.g., credential exposure, command injection in pipeline steps)

### What to expect

- Acknowledgment of your report within 48 hours
- An assessment of the vulnerability and a plan for a fix
- Credit in the fix commit (unless you prefer to remain anonymous)

## Scope

Security issues in this repository typically involve:

- Hardcoded credentials, tokens, or internal infrastructure details in templates
- Command injection risks in pipeline step scripts
- Insecure default configurations that could expose secrets
- Template logic that could leak environment variables or sensitive data

## Supported Versions

Only the latest version on the `main` branch is actively maintained with security fixes.
