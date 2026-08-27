from __future__ import annotations

TURN_TRACES_TABLE = "turn_traces"

CREATE_TURN_TRACES_TABLE = f"""
CREATE TABLE IF NOT EXISTS {TURN_TRACES_TABLE}
(
    organization_id   UUID,
    session_id        String,
    run_id            UUID,
    turn_id           Int32,
    timestamp         DateTime64(3, 'UTC'),
    speaker           Enum8('user' = 1, 'agent' = 2),
    turn_text         String,
    token_count       Int32,
    latency_ms        Float64,
    model_name        String,
    chaos_injected    String,
    scores            String,
    metadata          String
)
ENGINE = ReplacingMergeTree()
PARTITION BY (organization_id, toYYYYMM(timestamp))
ORDER BY (organization_id, session_id, turn_id, timestamp)
SETTINGS index_granularity = 8192
"""

CREATE_TURN_TRACES_DISTRIBUTED = f"""
CREATE TABLE IF NOT EXISTS {TURN_TRACES_TABLE}_distributed
(
    organization_id   UUID,
    session_id        String,
    run_id            UUID,
    turn_id           Int32,
    timestamp         DateTime64(3, 'UTC'),
    speaker           Enum8('user' = 1, 'agent' = 2),
    turn_text         String,
    token_count       Int32,
    latency_ms        Float64,
    model_name        String,
    chaos_injected    String,
    scores            String,
    metadata          String
)
ENGINE = Distributed('{TURN_TRACES_TABLE}_cluster', 'snt_ai', '{TURN_TRACES_TABLE}', rand())
"""

INSERT_TURN_TRACE = f"""
INSERT INTO {TURN_TRACES_TABLE}
(organization_id, session_id, run_id, turn_id, timestamp, speaker, turn_text,
 token_count, latency_ms, model_name, chaos_injected, scores, metadata)
VALUES
(%(organization_id)s, %(session_id)s, %(run_id)s, %(turn_id)s, %(timestamp)s, %(speaker)s, %(turn_text)s,
 %(token_count)s, %(latency_ms)s, %(model_name)s, %(chaos_injected)s, %(scores)s, %(metadata)s)
"""

QUERY_TRACES_BY_RUN = f"""
SELECT
    session_id,
    turn_id,
    timestamp,
    speaker,
    turn_text,
    token_count,
    latency_ms,
    model_name,
    chaos_injected,
    scores,
    metadata
FROM {TURN_TRACES_TABLE}
WHERE organization_id = %(organization_id)s
  AND run_id = %(run_id)s
ORDER BY session_id, turn_id ASC
"""

QUERY_AGGREGATE_METRICS_BY_RUN = f"""
SELECT
    run_id,
    count(*)                                     AS total_turns,
    avg(latency_ms)                              AS avg_latency_ms,
    quantile(0.50)(latency_ms)                   AS p50_latency_ms,
    quantile(0.90)(latency_ms)                   AS p90_latency_ms,
    quantile(0.99)(latency_ms)                   AS p99_latency_ms,
    sum(token_count)                             AS total_tokens,
    avg(token_count)                             AS avg_tokens_per_turn,
    countDistinct(session_id)                    AS total_sessions
FROM {TURN_TRACES_TABLE}
WHERE organization_id = %(organization_id)s
  AND run_id = %(run_id)s
GROUP BY run_id
"""

QUERY_COMPLIANCE_BREAKDOWN = f"""
SELECT
    run_id,
    JSONExtractString(scores, 'groundedness')    AS groundedness_score,
    JSONExtractString(scores, 'compliance')      AS compliance_score,
    JSONExtractString(scores, 'robustness')      AS robustness_score,
    count(*)                                     AS turn_count
FROM {TURN_TRACES_TABLE}
WHERE organization_id = %(organization_id)s
  AND run_id = %(run_id)s
  AND speaker = 'agent'
GROUP BY run_id, groundedness_score, compliance_score, robustness_score
"""

QUERY_REGRESSION_DELTA = f"""
WITH current_run AS (
    SELECT
        avg(JSONExtractFloat(scores, 'groundedness')) AS g,
        avg(JSONExtractFloat(scores, 'compliance'))   AS c,
        avg(JSONExtractFloat(scores, 'robustness'))   AS r,
        quantile(0.90)(latency_ms)                    AS p90_lat
    FROM {TURN_TRACES_TABLE}
    WHERE run_id = %(current_run_id)s
),
baseline_run AS (
    SELECT
        avg(JSONExtractFloat(scores, 'groundedness')) AS g,
        avg(JSONExtractFloat(scores, 'compliance'))   AS c,
        avg(JSONExtractFloat(scores, 'robustness'))   AS r,
        quantile(0.90)(latency_ms)                    AS p90_lat
    FROM {TURN_TRACES_TABLE}
    WHERE run_id = %(baseline_run_id)s
)
SELECT
    current_run.g - baseline_run.g     AS groundedness_delta,
    current_run.c - baseline_run.c     AS compliance_delta,
    current_run.r - baseline_run.r     AS robustness_delta,
    current_run.p90_lat - baseline_run.p90_lat AS p90_latency_delta
FROM current_run, baseline_run
"""
