export interface Organization {
  id: string;
  name: string;
  slug: string;
  billing_plan: "free" | "pro" | "enterprise";
  settings: string | null;
  is_active: boolean;
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  organization_id: string;
  role: "admin" | "member" | "viewer";
  is_active: boolean;
  created_at: string;
}

export interface TargetAgent {
  id: string;
  name: string;
  model_name: string;
  system_prompt: string;
  agent_type: "chat" | "rag" | "agentic";
  organization_id: string;
  version: number;
  created_at: string;
}

export interface EvaluationSuite {
  id: string;
  name: string;
  description: string | null;
  target_agent_id: string;
  organization_id: string;
  persona_config: PersonaConfig[];
  chaos_profiles: ChaosProfileConfig;
  judge_config: JudgeConfig;
  is_active: boolean;
  created_at: string;
}

export interface PersonaConfig {
  name: string;
  category: "standard" | "edge_case" | "adversarial";
  initial_user_intent: string;
  emotional_state: string;
}

export interface ChaosProfileConfig {
  latency_percentile_75_ms?: number;
  latency_percentile_99_ms?: number;
  timeout_seconds?: number;
  context_bloat_factor?: number;
  guardrail_interruption_rate?: number;
  prompt_injection_attempt_rate?: number;
}

export interface JudgeConfig {
  use_llm_fallback?: boolean;
  llm_model?: string;
  pass_thresholds?: {
    groundedness: number;
    compliance: number;
    robustness: number;
  };
}

export interface RunMetadata {
  id: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  total_sessions: number;
  completed_sessions: number;
  aggregate_score: number | null;
  summary_metrics: Record<string, unknown> | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface TurnVerdict {
  turn_index: number;
  pass: boolean;
  scores: {
    groundedness: number;
    compliance: number;
    robustness: number;
    overall: number;
  };
  rubric: {
    groundedness: string[];
    compliance: string[];
    robustness: string[];
  };
  detected_issues: string[];
}

export interface SessionVerdict {
  session_id: string;
  persona_name: string;
  aggregate_score: number;
  turn_count: number;
  pass_count: number;
  turn_verdicts: TurnVerdict[];
}

export interface TurnTrace {
  session_id: string;
  turn_id: number;
  timestamp: string;
  speaker: string;
  turn_text: string;
  token_count: number;
  latency_ms: number;
  model_name: string;
  chaos_injected: Record<string, unknown>;
  scores: Record<string, number>;
  metadata: Record<string, unknown>;
}

export interface TraceQueryResponse {
  turns: TurnTrace[];
  total: number;
}

export interface RunMetricsResponse {
  run_id: string;
  total_turns: number;
  avg_latency_ms: number;
  p50_latency_ms: number;
  p90_latency_ms: number;
  p99_latency_ms: number;
  total_tokens: number;
  avg_tokens_per_turn: number;
  total_sessions: number;
}

export interface DeltaMetric {
  metric: string;
  current_value: number;
  baseline_value: number;
  delta: number;
  delta_percentage: number;
  regressed: boolean;
}

export interface RegressionDeltaResponse {
  deltas: DeltaMetric[];
}

export interface BillingPlan {
  plan: "free" | "pro" | "enterprise";
}

export interface MemberResponse {
  id: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface UsageResponse {
  total_runs: number;
  completed_runs: number;
  failed_runs: number;
  total_sessions: number;
  active_members: number;
}
