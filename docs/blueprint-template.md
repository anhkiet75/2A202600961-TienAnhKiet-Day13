# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: C5
- [REPO_URL]: https://github.com/anhkiet75/2A202600961-TienAnhKiet-Day13
- [MEMBERS]:
  - Member A: Tiền Anh Kiệt | Role: Logging & PII & Tracing & SLO & Alerts & Dashboard

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 10+
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: data/screenshots/EVIDENCE_CORRELATION_ID_SCREENSHOT.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: data/screenshots/EVIDENCE_PII_REDACTION_SCREENSHOT.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: data/screenshots/EVIDENCE_TRACE_WATERFALL_SCREENSHOT.png
- [TRACE_WATERFALL_EXPLANATION]: The `LabAgent.run` method is decorated with `@observe()`, so each request produces one root span on the waterfall that wraps the full pipeline (RAG retrieval + LLM generation). The span carries metadata (`doc_count`, `query_preview`) and token usage. Under normal conditions `LabAgent.run` completes in ~100ms, but when the `rag_slow` incident is enabled the RAG retrieval step inside it blocks for 2500ms+, so the span's total duration balloons and shows up on the waterfall as a very wide horizontal bar — directly explaining why P95 latency exceeds the 3000ms SLO.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: data/screenshots/DASHBOARD_6_PANELS_SCREENSHOT.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 155ms |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | $0.0294 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: data/screenshots/ALERT_RULES_SCREENSHOT.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 latency jumped from ~155ms to ~2660ms after enabling `rag_slow` incident. Quality score dropped from 0.88 to 0.7 due to empty RAG context. Dashboard showed latency SLO breach immediately.
- [ROOT_CAUSE_PROVED_BY]: Trace waterfall showed RAG span consuming 2500ms+ vs normal 100ms. Log line: `{"event": "request_failed", "latency_ms": 2660, "correlation_id": "req-..."}`. Confirmed via `curl http://127.0.0.1:8000/health` → `"rag_slow": true`.
- [FIX_ACTION]: Disabled incident toggle via `python scripts/inject_incident.py --scenario rag_slow --disable`. Latency returned to ~155ms P95 within next request batch.
- [PREVENTIVE_MEASURE]: Add circuit breaker on RAG retrieval with 500ms timeout fallback to empty context. Alert `high_latency_p95` (docs/alerts.md#1) fires within 5m of breach to notify oncall.

---

## 5. Individual Contributions & Evidence

### Tien Anh Kiet
- [TASKS_COMPLETED]: Implemented all 4 code TODOs: (1) CorrelationIdMiddleware — clears contextvars between requests, generates IDs in the `req-<8-hex>` format, binds them into the structlog context and attaches them to the response header; (2) Log enrichment — binds `user_id_hash`, `session_id`, `feature`, `model` to every request to `/chat`; (3) PII scrubbing — enabled the `scrub_event` processor in the structlog pipeline to automatically redact emails, phone numbers, CCCD, credit cards, and passports; (4) Extended PII patterns — added passport regex and Vietnamese address keywords. Additionally: fixed Langfuse v3 compatibility in `tracing.py`, configured 4 alert rules with runbook links in `config/alert_rules.yaml`, built a 6-panel dashboard auto-refreshing every 15 seconds at `data/dashboard.html`, and separated audit logs at `data/audit.jsonl` via the `app/audit.py` module.
- [EVIDENCE_LINK]: https://github.com/anhkiet75/2A202600961-TienAnhKiet-Day13/commit/61ddf64d11ab813df654b95ddf1b06ed55815b74

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Per-request cost tracking via `_estimate_cost()` in `app/agent.py` (input × $3/M + output × $15/M tokens). Exposed at `GET /metrics` as `avg_cost_usd` and `total_cost_usd`. Visualized in dashboard Cost panel with SLO `< $2.50/day`. Alert rule `cost_budget_spike` fires when hourly cost exceeds 2× baseline for 15m — runbook: `docs/alerts.md#3-cost-budget-spike`.
- [BONUS_AUDIT_LOGS]: Audit logs are kept separately at `data/audit.jsonl` (distinct from `data/logs.jsonl`). The `app/audit.py` module writes each entry with a fixed schema: `ts`, `action`, `actor` (user_id_hash), `outcome`, and action-specific metadata. Audited events: `/chat` requests (success/error, with `correlation_id`, `feature`, `latency_ms`, `cost_usd`), `incident_enable`, and `incident_disable`. PII-safe: the actor uses a hash instead of the real user_id.
- [BONUS_CUSTOM_METRIC]: `quality_score` — heuristic business metric computed in `app/agent.py::_heuristic_quality()`: base 0.5, +0.2 if RAG docs retrieved, +0.1 if answer length > 40 chars, +0.1 if keyword overlap with question, −0.2 if PII leaked into answer. Aggregated as `quality_avg` in `GET /metrics`, visualized in dashboard panel 6 with SLO `> 0.75`, and alert `quality_degradation` fires when avg < 0.75 for 10m.
