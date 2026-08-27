"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/auth-context";
import type { RunMetadata, EvaluationSuite } from "@/types";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area,
} from "recharts";
import { TrendingUp, TrendingDown, AlertCircle, Inbox } from "lucide-react";
import { formatScore } from "@/lib/utils";

function computeMetrics(runs: RunMetadata[]) {
  const valid = runs.filter(Boolean);
  const total = valid.length;
  const completed = valid.filter((r) => r.status === "completed");
  const scores = completed.map((r) => r.aggregate_score ?? 0);
  const avgScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
  const totalSessions = valid.reduce((s, r) => s + r.total_sessions, 0);
  const passRate = scores.filter((s) => s >= 0.7).length / (scores.length || 1);
  return { totalEvaluations: total, avgScore, totalSessions, passRate };
}

function MetricCard({
  title, value, subtitle, trend, loading,
}: {
  title: string; value: string; subtitle: string; trend?: "up" | "down"; loading?: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        {trend && !loading && (
          <span className={trend === "up" ? "text-emerald-500" : "text-red-500"}>
            {trend === "up" ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
          </span>
        )}
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-24 mb-1" />
        ) : (
          <div className="text-2xl font-bold">{value}</div>
        )}
        <p className="text-xs text-muted-foreground">{subtitle}</p>
      </CardContent>
    </Card>
  );
}

export function MetricCards() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const { data: runs, loading, error } = useApi(
    () => api.evaluations.list(orgId),
    [] as RunMetadata[],
  );

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800 flex items-center gap-2">
        <AlertCircle className="h-4 w-4" />
        Failed to load metrics: {error}
      </div>
    );
  }

  const metrics = runs && runs.length > 0
    ? computeMetrics(runs)
    : { totalEvaluations: 0, avgScore: 0, totalSessions: 0, passRate: 0 };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <MetricCard title="Total Evaluations" value={metrics.totalEvaluations.toString()} subtitle="All time" trend="up" loading={loading} />
      <MetricCard title="Average Score" value={formatScore(metrics.avgScore)} subtitle="Across all runs" loading={loading} />
      <MetricCard title="Total Sessions" value={metrics.totalSessions.toLocaleString()} subtitle="Conversations evaluated" trend="up" loading={loading} />
      <MetricCard title="Pass Rate" value={formatScore(metrics.passRate)} subtitle="Above threshold" loading={loading} />
    </div>
  );
}

export function ScoreChart() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const { data: runs, loading, error } = useApi(
    () => api.evaluations.list(orgId),
    [] as RunMetadata[],
  );

  const trendData = runs && runs.length > 0
    ? [...runs]
        .reverse()
        .slice(-7)
        .map((r) => ({
          date: r.started_at ? new Date(r.started_at).toLocaleDateString("en-US", { weekday: "short" }) : "?",
          score: r.aggregate_score ?? 0,
        }))
    : [];

  const hasData = trendData.length > 0;

  return (
    <Card className="col-span-2">
      <CardHeader>
        <CardTitle className="text-base">Score Trend {hasData ? "(Last 7 Runs)" : ""}</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-[200px] w-full" />
        ) : error ? (
          <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground gap-2">
            <AlertCircle className="h-4 w-4 text-red-500" />
            Failed to load trend
          </div>
        ) : !hasData ? (
          <div className="flex h-[200px] flex-col items-center justify-center text-muted-foreground">
            <Inbox className="h-8 w-8 mb-2" />
            <p className="text-sm">No run data yet</p>
          </div>
        ) : (
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#888888" fontSize={12} />
                <YAxis stroke="#888888" fontSize={12} domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip formatter={(value: number) => `${(value * 100).toFixed(1)}%`} />
                <Area type="monotone" dataKey="score" stroke="#3b82f6" fill="url(#scoreGradient)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function CategoryChart() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const { data: suites, loading, error } = useApi(
    () => api.suites.list(orgId),
    [] as EvaluationSuite[],
  );

  const categoryCounts: { name: string; count: number }[] = (suites && suites.length > 0
    ? (() => {
        const counts: Record<string, number> = {};
        for (const s of suites) {
          const configs = s.persona_config || [];
          for (const pc of configs) {
            const cat = pc.category || "standard";
            counts[cat] = (counts[cat] || 0) + 1;
          }
        }
        return Object.entries(counts).map(([name, count]) => ({
          name: name.charAt(0).toUpperCase() + name.slice(1).replace("_", " "),
          count,
        }));
      })()
    : []);

  const hasData = categoryCounts.length > 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Personas by Category</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-[200px] w-full" />
        ) : error ? (
          <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground gap-2">
            <AlertCircle className="h-4 w-4 text-red-500" />
            Failed to load categories
          </div>
        ) : !hasData ? (
          <div className="flex h-[200px] flex-col items-center justify-center text-muted-foreground">
            <Inbox className="h-8 w-8 mb-2" />
            <p className="text-sm">No persona data</p>
          </div>
        ) : (
          <div className="h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryCounts}>
                <XAxis dataKey="name" stroke="#888888" fontSize={12} />
                <YAxis stroke="#888888" fontSize={12} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
