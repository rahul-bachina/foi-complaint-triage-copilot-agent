#!/usr/bin/env python3
"""Validate the permissions manifest and the triage output schema."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft7Validator, validate

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    manifest_schema = json.loads((ROOT / "schemas" / "agent-manifest.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(manifest_schema)
    print("Agent manifest schema is valid Draft-07")

    manifest = yaml.safe_load((ROOT / "agent-manifest.yaml").read_text(encoding="utf-8"))
    validate(instance=manifest, schema=manifest_schema)
    print("agent-manifest.yaml matches the schema")

    if manifest.get("$schema") != "schemas/agent-manifest.schema.json":
        print("Manifest $schema must point at schemas/agent-manifest.schema.json", file=sys.stderr)
        return 1
    level = manifest["autonomy"]["level"]
    if level not in {"A0", "A1", "A2"}:
        print(f"Autonomy level {level} is outside A0-A2", file=sys.stderr)
        return 1
    if manifest["autonomy"].get("auto_actions_enabled") is not False:
        print("auto_actions_enabled must stay false", file=sys.stderr)
        return 1
    if manifest["tools"]["writes"].get("enabled") is not False:
        print("writes must stay disabled", file=sys.stderr)
        return 1
    if manifest["tools"]["sends"].get("enabled") is not False:
        print("sends must stay disabled", file=sys.stderr)
        return 1
    for name, action in manifest["high_risk_actions"].items():
        if action.get("enabled") is not False:
            print(f"High-risk action {name} must stay disabled", file=sys.stderr)
            return 1

    output_schema = json.loads((ROOT / "schema" / "triage_output.schema.json").read_text(encoding="utf-8"))
    Draft7Validator.check_schema(output_schema)
    print("Triage output schema is valid Draft-07")
    sample = json.loads((ROOT / "examples" / "sample_output.json").read_text(encoding="utf-8"))
    validate(instance=sample, schema=output_schema)
    print("examples/sample_output.json matches the triage schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
