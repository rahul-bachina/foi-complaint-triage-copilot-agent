# Microsoft Foundry

This folder is the live-model note for the same Python triage core. There is no Foundry project file to import, and this repository does not create a Foundry resource.

The path this repository tests is mock mode: `python src/triage_agent.py --mock`. A live call is the same command without `--mock`.

## Live call

`src/triage_agent.py` uses the `openai` SDK against a deployment you create. Set these in your own environment. Do not commit them.

| Variable | Purpose |
| --- | --- |
| `AZURE_OPENAI_ENDPOINT` | Endpoint of your resource |
| `AZURE_OPENAI_API_KEY` | Key, if you are not using Microsoft Entra ID |
| `AZURE_OPENAI_DEPLOYMENT` | Deployment name. The experiment notes use `gpt-4o` as an example, not as a requirement |

If the key is unset, the client uses `DefaultAzureCredential`. That still needs an endpoint.

The product was formerly called Azure AI Foundry. Current name and scope: [What is Microsoft Foundry?](https://learn.microsoft.com/en-us/azure/foundry/what-is-foundry)

## What you still have to turn on

The [security and permissions guide](../docs/security-and-permissions.md) names prompt shields, Key Vault, private networking, Microsoft Entra ID, and a UK region. This repository does not enable them. The manifest assumes production inference in UK South or UK West. That is for the deploying organisation to confirm before any real submission is processed.

Use the synthetic files in `examples/` and `eval/`. Do not paste a live request into a shared environment.

## Copilot Studio

The standard harness calls Microsoft Foundry from a Power Automate flow. The build steps are in [../copilot-studio/power-automate-flow.md](../copilot-studio/power-automate-flow.md). That is a guide, not a solution package.

The GitHub Copilot harness, which is a Copilot Studio runtime and not the GitHub Copilot product, can call the same `triage()` function. See [../docs/github-copilot-harness.md](../docs/github-copilot-harness.md).
