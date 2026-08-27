CREATE DATABASE IF NOT EXISTS snt_ai;

CREATE TABLE IF NOT EXISTS snt_ai.turn_traces
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
SETTINGS index_granularity = 8192;
