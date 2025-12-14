#!/usr/bin/env bash
set -euo pipefail

CASES_PATH="${1:-../data/synthetic_cases.jsonl}"

echo "Running synthetic cases from: $CASES_PATH"

python - "$CASES_PATH" << 'EOF'
import sys
import json
from pathlib import Path

from dundieplz.extract.extractor import Extractor
from dundieplz.extract.rule_llm_client import RuleLLMClient

cases_path = Path(sys.argv[1])
lines = [ln for ln in cases_path.read_text(encoding="utf-8").splitlines() if ln.strip()]

rule_client = RuleLLMClient()
extractor = Extractor(llm_client=rule_client)

def got_dict(result):
    s = result.signals
    return {
        "suicidal_ideation": s.suicidal_ideation.presence.value,
        "intent": s.intent.presence.value,
        "plan": s.plan.presence.value,
        "past_behavior": s.past_behavior.presence.value,
        "temporal": s.temporal.value,
    }

for ln in lines:
    case = json.loads(ln)
    text = case["text"]

    # --- DEBUG 1: call RuleLLMClient directly (bypasses Extractor) ---
    direct = rule_client.generate_json(text)

    # --- DEBUG 2: call Extractor (should internally call the client) ---
    result = extractor.extract(text)

    expected = case.get("expected", {})
    got = got_dict(result)

    print("\n" + "=" * 60)
    print("CASE:", case.get("case_id"))
    print("Expected:", expected)

    print("\n[DEBUG] RuleLLMClient.generate_json(text) returned:")
    print({k: direct.get(k) for k in ["suicidal_ideation","intent","plan","past_behavior","temporal"]})

    print("\nGot (Extractor output):", got)

    keys = sorted(set(expected.keys()) | set(got.keys()))
    for k in keys:
        if k in expected and got.get(k) != expected.get(k):
            print(f"  FAIL {k}: expected={expected[k]} got={got.get(k)}")
        elif k in expected:
            print(f"  PASS {k}: {expected[k]}")

print("\nTest completed.")
EOF
