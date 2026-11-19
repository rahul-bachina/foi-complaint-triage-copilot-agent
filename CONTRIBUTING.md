# Contributing

This is a standalone copy of one experiment. Changes should keep it runnable from the repository root, on synthetic data, with a person still making the decision.

## Before you open a pull request

```bash
python -m pip install -r requirements.txt
python -m pytest tests/ -v --tb=short
python scripts/validate_schemas.py
python scripts/governance_check.py
python scripts/build_llms_full.py
```

Use UK English in docs you add. Use the name Microsoft Foundry. The retired product name is allowed only on a line that says the product was formerly called that.

Do not add real requests, personal data, or secrets. New examples belong in `examples/` or `eval/` and must be obviously synthetic.

Do not enable sends, writes, or an autonomy level above A2. A0, A1, and A2 are defined in `docs/autonomy-levels.md`. This agent is A1. If a change affects what the agent may do, update `agent-manifest.yaml` and `docs/security-and-permissions.md` in the same pull request.

## Hub sync

Weekly sync pull requests come from `.github/workflows/sync-from-hub.yml`. Review them. They refresh the experiment files and then rewrite standalone paths. They must not overwrite the files listed in `.sync-ignore`, including this file and `README.md`.

## Adaptation requests

If you want this built for your organisation, open a [request an adaptation](https://github.com/rahul-bachina/foi-complaint-triage-copilot-agent/issues/new?template=request-an-adaptation.yml) issue. Do not attach live case files.
