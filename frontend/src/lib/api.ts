const API_BASE = "/api/v1";

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem("snt_auth_token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${endpoint}`;
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...options?.headers,
    },
    ...options,
  });

  if (res.status === 401) {
    throw new Error("Session expired. Please log in again.");
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

export const api = {
  evaluations: {
    list: (orgId: string, page = 1, perPage = 20) =>
      request<import("@/types").RunMetadata[]>(
        `/evaluations/runs?page=${page}&per_page=${perPage}`
      ),
    get: (orgId: string, runId: string) =>
      request<import("@/types").RunMetadata>(
        `/evaluations/runs/${runId}`
      ),
    run: (payload: {
      suite_id: string;
      agent_id: string;
      description?: string;
    }) =>
      request<import("@/types").RunMetadata>("/evaluations/run", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    webhookRun: (payload: {
      suite_id: string;
      agent_id: string;
      source: string;
      branch?: string;
      commit_sha?: string;
      pr_number?: number;
    }) =>
      request<{
        run_id: string;
        status: string;
        suite_name: string;
        aggregate_score: number;
        total_sessions: number;
        completed_sessions: number;
        report_junit: string;
      }>("/evaluations/webhook/run", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    getTraces: (orgId: string, runId: string) =>
      request<{ turns: import("@/types").TurnTrace[]; total: number }>(
        `/evaluations/traces/${runId}`
      ),
    getMetrics: (orgId: string, runId: string) =>
      request<{
        run_id: string;
        total_turns: number;
        avg_latency_ms: number;
        p50_latency_ms: number;
        p90_latency_ms: number;
        p99_latency_ms: number;
        total_tokens: number;
        avg_tokens_per_turn: number;
        total_sessions: number;
      }>(`/evaluations/metrics/${runId}`),
    compare: (
      orgId: string,
      currentRunId: string,
      baselineRunId: string
    ) =>
      request<{
        deltas: Array<{
          metric: string;
          current_value: number;
          baseline_value: number;
          delta: number;
          delta_percentage: number;
          regressed: boolean;
        }>;
      }>("/evaluations/regression-delta", {
        method: "POST",
        body: JSON.stringify({
          current_run_id: currentRunId,
          baseline_run_id: baselineRunId,
        }),
      }),
    getReport: (runId: string, format: "summary" | "junit" = "summary") => {
      const url = `${API_BASE}/evaluations/runs/${runId}/report?format=${format}`;
      const token = typeof window !== "undefined" ? localStorage.getItem("snt_auth_token") : null;
      return fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      }).then((res) => {
        if (!res.ok) throw new Error(`Report fetch failed: ${res.status}`);
        return res.text();
      });
    },
  },
  suites: {
    list: (orgId: string) =>
      request<{ items: import("@/types").EvaluationSuite[]; total: number }>(
        `/suites?organization_id=${orgId}`
      ).then(r => r.items),
    get: (orgId: string, suiteId: string) =>
      request<import("@/types").EvaluationSuite>(
        `/suites/${suiteId}`
      ),
    create: (payload: Partial<import("@/types").EvaluationSuite>) =>
      request<import("@/types").EvaluationSuite>("/suites", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },
  agents: {
    list: (orgId: string) =>
      request<{ items: import("@/types").TargetAgent[]; total: number }>(
        `/agents?organization_id=${orgId}`
      ).then(r => r.items),
    get: (orgId: string, agentId: string) =>
      request<import("@/types").TargetAgent>(
        `/agents/${agentId}`
      ),
    create: (payload: Partial<import("@/types").TargetAgent>) =>
      request<import("@/types").TargetAgent>("/agents", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
  },
  org: {
    get: () => request<import("@/types").Organization>("/organizations/me"),
    update: (payload: { name?: string; settings?: string }) =>
      request<import("@/types").Organization>("/organizations/me", {
        method: "PATCH", body: JSON.stringify(payload),
      }),
    members: () => request<import("@/types").MemberResponse[]>("/organizations/me/members"),
    usage: () => request<import("@/types").UsageResponse>("/organizations/me/usage"),
    billing: () => request<import("@/types").BillingPlan>("/organizations/me/billing"),
  },
  auth: {
    me: () => request<import("@/types").User>("/auth/me"),
  },
};
