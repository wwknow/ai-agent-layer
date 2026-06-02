#!/usr/bin/env bash
set -euo pipefail

cd /opt/ai-agent-layer

OUT="state/checks/runtime.json"
mkdir -p "$(dirname "$OUT")"

MASTER_KEY="$(grep '^LITELLM_MASTER_KEY=' .env | cut -d= -f2- || true)"

AGENT_HEALTH_BODY="$(mktemp)"
LITELLM_MODELS_BODY="$(mktemp)"
AGENT_RUN_BODY="$(mktemp)"

AGENT_HEALTH_CODE="$(curl -sS --max-time 20 -o "$AGENT_HEALTH_BODY" -w '%{http_code}' http://127.0.0.1:8088/health || true)"

LITELLM_MODELS_CODE="$(curl -sS --max-time 30 -o "$LITELLM_MODELS_BODY" -w '%{http_code}' \
  http://127.0.0.1:4000/models \
  -H "Authorization: Bearer ${MASTER_KEY}" || true)"

AGENT_RUN_CODE="$(curl -sS --max-time 90 -o "$AGENT_RUN_BODY" -w '%{http_code}' \
  http://127.0.0.1:8088/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task_type":"code_generate","prompt":"只回复：VERIFY_OK"}' || true)"

SENSITIVE_TRACKED="$(git ls-files | grep -E '(^\.env$|litellm-config.yaml|postgres-data|redis-data|workspaces|screenshots|cookies)' || true)"

python3 - <<PY
import json, pathlib

agent_health_code = "$AGENT_HEALTH_CODE"
litellm_models_code = "$LITELLM_MODELS_CODE"
agent_run_code = "$AGENT_RUN_CODE"
sensitive_tracked = """$SENSITIVE_TRACKED""".strip()

agent_health_body = pathlib.Path("$AGENT_HEALTH_BODY").read_text(errors="ignore")
litellm_models_body = pathlib.Path("$LITELLM_MODELS_BODY").read_text(errors="ignore")
agent_run_body = pathlib.Path("$AGENT_RUN_BODY").read_text(errors="ignore")

checks = {
    "agent_health_ok": agent_health_code == "200" and '"status":"ok"' in agent_health_body,
    "litellm_models_ok": litellm_models_code == "200" and "code_fast" in litellm_models_body,
    "agent_run_ok": agent_run_code == "200" and "VERIFY_OK" in agent_run_body,
    "no_sensitive_files_tracked": sensitive_tracked == "",
}

result = {
    "agent_health_code": agent_health_code,
    "litellm_models_code": litellm_models_code,
    "agent_run_code": agent_run_code,
    "checks": checks,
    "pass": all(checks.values()),
    "ship_ok": all(checks.values()),
    "sensitive_tracked": sensitive_tracked,
}

pathlib.Path("$OUT").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
PY

rm -f "$AGENT_HEALTH_BODY" "$LITELLM_MODELS_BODY" "$AGENT_RUN_BODY"
