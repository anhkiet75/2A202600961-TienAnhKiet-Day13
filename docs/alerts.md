# Alert Rules and Runbooks

## 1. High latency P95
- Severity: P2
- Trigger: `latency_p95_ms > 3000 for 5m`
- Impact: tail latency breaches SLO
- First checks:
  1. Open top slow traces in the last 1h
  2. Compare RAG span vs LLM span
  3. Check if incident toggle `rag_slow` is enabled
- Mitigation:
  - truncate long queries
  - fallback retrieval source
  - lower prompt size

## 2. High error rate
- Severity: P1
- Trigger: `error_rate_pct > 2 for 5m`
- Impact: users receive failed responses
- First checks:
  1. Group logs by `error_type`
  2. Inspect failed traces
  3. Determine whether failures are LLM, tool, or schema related
- Mitigation:
  - rollback latest change
  - disable failing tool
  - retry with fallback model

## 3. Cost budget spike
- Severity: P2
- Trigger: `hourly_cost_usd > 2x_baseline for 15m`
- Impact: burn rate exceeds budget
- First checks:
  1. Split traces by feature and model
  2. Compare tokens_in/tokens_out
  3. Check if `cost_spike` incident was enabled
- Mitigation:
  - shorten prompts
  - route easy requests to cheaper model
  - apply prompt cache

## 4. Quality degradation
- Severity: P2
- Trigger: `quality_score_avg < 0.75 for 10m`
- Impact: users receive low-quality answers below SLO target
- First checks:
  1. Check quality_score distribution in recent traces on Langfuse
  2. Compare RAG doc_count — low retrieval = low quality
  3. Check if `rag_slow` incident toggle causes empty docs
  4. Review `logs.jsonl` for `[REDACTED` in answers (over-scrubbing)
- Mitigation:
  - re-enable retrieval if `rag_slow` was toggled
  - expand retrieval top-k
  - review PII regex to avoid over-redacting answer content
