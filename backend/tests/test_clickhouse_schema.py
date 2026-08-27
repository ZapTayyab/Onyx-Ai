from __future__ import annotations

from app.models.clickhouse.traces import (
    CREATE_TURN_TRACES_TABLE,
    INSERT_TURN_TRACE,
    QUERY_AGGREGATE_METRICS_BY_RUN,
    QUERY_COMPLIANCE_BREAKDOWN,
    QUERY_REGRESSION_DELTA,
    QUERY_TRACES_BY_RUN,
    TURN_TRACES_TABLE,
)


class TestClickHouseSchema:
    def test_table_name(self) -> None:
        assert TURN_TRACES_TABLE == "turn_traces"

    def test_create_table_sql_contains_required_columns(self) -> None:
        required_columns = [
            "organization_id",
            "session_id",
            "run_id",
            "turn_id",
            "timestamp",
            "speaker",
            "turn_text",
            "token_count",
            "latency_ms",
            "chaos_injected",
            "scores",
            "metadata",
        ]
        for col in required_columns:
            assert col in CREATE_TURN_TRACES_TABLE, f"Missing column: {col}"

    def test_create_table_uses_replacing_merge_tree(self) -> None:
        assert "ReplacingMergeTree()" in CREATE_TURN_TRACES_TABLE

    def test_create_table_partitioned_by_org_and_month(self) -> None:
        assert "PARTITION BY (organization_id, toYYYYMM(timestamp))" in CREATE_TURN_TRACES_TABLE

    def test_insert_query_has_all_placeholders(self) -> None:
        expected_placeholders = [
            "organization_id",
            "session_id",
            "run_id",
            "turn_id",
            "timestamp",
            "speaker",
            "turn_text",
            "token_count",
            "latency_ms",
            "chaos_injected",
            "scores",
            "metadata",
        ]
        for ph in expected_placeholders:
            assert f"%({ph})s" in INSERT_TURN_TRACE, f"Missing placeholder: {ph}"

    def test_trace_query_includes_org_filter(self) -> None:
        assert "%(organization_id)s" in QUERY_TRACES_BY_RUN
        assert "ORDER BY session_id, turn_id ASC" in QUERY_TRACES_BY_RUN

    def test_metrics_query_includes_latency_percentiles(self) -> None:
        assert "quantile(0.50)" in QUERY_AGGREGATE_METRICS_BY_RUN
        assert "quantile(0.90)" in QUERY_AGGREGATE_METRICS_BY_RUN
        assert "quantile(0.99)" in QUERY_AGGREGATE_METRICS_BY_RUN

    def test_compliance_breakdown_extracts_json_scores(self) -> None:
        assert "JSONExtractString(scores, 'groundedness')" in QUERY_COMPLIANCE_BREAKDOWN
        assert "JSONExtractString(scores, 'compliance')" in QUERY_COMPLIANCE_BREAKDOWN
        assert "JSONExtractString(scores, 'robustness')" in QUERY_COMPLIANCE_BREAKDOWN

    def test_regression_delta_requires_two_run_ids(self) -> None:
        assert "%(current_run_id)s" in QUERY_REGRESSION_DELTA
        assert "%(baseline_run_id)s" in QUERY_REGRESSION_DELTA

    def test_regression_delta_calculates_deltas(self) -> None:
        assert "groundedness_delta" in QUERY_REGRESSION_DELTA
        assert "compliance_delta" in QUERY_REGRESSION_DELTA
        assert "robustness_delta" in QUERY_REGRESSION_DELTA
        assert "p90_latency_delta" in QUERY_REGRESSION_DELTA
