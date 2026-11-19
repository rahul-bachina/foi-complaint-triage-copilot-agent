# Security

This repository is a reference implementation and a build guide. It is not a hosted service, and it does not contain production submissions.

## Report a vulnerability

Use GitHub private vulnerability reporting:

https://github.com/rahul-bachina/foi-complaint-triage-copilot-agent/security/advisories/new

Do not open a public issue, pull request, or discussion that includes:

- a live FOI request, complaint, or subject access request
- personal data, special-category data, or a real case reference
- API keys, connection strings, or tenant identifiers

If private reporting is unavailable, contact Rahul Bachina through GitHub: https://github.com/rahul-bachina

## What this code is allowed to do

The permissions manifest (`agent-manifest.yaml`) is the control. In short: autonomy A1, writes disabled, sends disabled, and the five high-risk actions disabled. A change that lets the agent send, write to a case system, or decide an information request is a security issue even if the tests still pass.

## Secrets

No cloud credentials belong in this repository. The live path reads `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_DEPLOYMENT` from the environment. CI runs a secret scan in `scripts/governance_check.py`. Placeholders such as `example.gov.uk` are not real inboxes.

## Data

Evaluation and example files are synthetic. Do not add real requests to fixtures, issues, or logs.
