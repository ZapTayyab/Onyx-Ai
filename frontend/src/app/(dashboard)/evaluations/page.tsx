"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { formatDate, formatScore, getScoreColor } from "@/lib/utils";
import { useAuth } from "@/contexts/auth-context";
import { Play, Plus, Clock, CheckCircle2, XCircle, RefreshCw, X, Loader2 } from "lucide-react";
import type { RunMetadata, EvaluationSuite, TargetAgent } from "@/types";

export default function EvaluationsPage() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const [activeTab, setActiveTab] = useState("all");
  const { data: runs, loading, refetch } = useApi(
    () => api.evaluations.list(orgId),
    [] as RunMetadata[],
  );

  const [showDialog, setShowDialog] = useState(false);
  const [selectedSuite, setSelectedSuite] = useState("");
  const [selectedAgent, setSelectedAgent] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  const { data: suites } = useApi(
    () => api.suites.list(orgId),
    [] as EvaluationSuite[],
  );

  const { data: agents } = useApi(
    () => api.agents.list(orgId),
    [] as TargetAgent[],
  );

  async function handleRun() {
    if (!selectedSuite || !selectedAgent) return;
    setSubmitting(true);
    setSubmitError("");
    try {
      await api.evaluations.run({
        suite_id: selectedSuite,
        agent_id: selectedAgent,
        description: description || undefined,
      });
      setShowDialog(false);
      setSelectedSuite("");
      setSelectedAgent("");
      setDescription("");
      refetch();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to start evaluation");
    } finally {
      setSubmitting(false);
    }
  }

  const displayRuns = runs ?? [];
  const filtered = activeTab === "all"
    ? displayRuns
    : displayRuns.filter((e) => e.status === activeTab);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Evaluations</h1>
          <p className="text-muted-foreground">Run and manage evaluation suites</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={refetch}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <Button onClick={() => setShowDialog(true)}>
            <Plus className="mr-2 h-4 w-4" /> New Evaluation
          </Button>
        </div>
      </div>

      {showDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-lg border bg-card p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">New Evaluation</h2>
              <Button variant="ghost" size="icon" onClick={() => setShowDialog(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Evaluation Suite</label>
                <select
                  value={selectedSuite}
                  onChange={(e) => setSelectedSuite(e.target.value)}
                  className="block w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="">Select a suite...</option>
                  {(suites ?? []).map((s) => (
                    <option key={s.id} value={s.id}>{s.name}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Target Agent</label>
                <select
                  value={selectedAgent}
                  onChange={(e) => setSelectedAgent(e.target.value)}
                  className="block w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                >
                  <option value="">Select an agent...</option>
                  {(agents ?? []).map((a) => (
                    <option key={a.id} value={a.id}>{a.name} ({a.model_name})</option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description (optional)</label>
                <Input
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="e.g., Regression test for v2.1"
                />
              </div>
              {submitError && (
                <p className="text-sm text-red-600">{submitError}</p>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setShowDialog(false)} disabled={submitting}>
                  Cancel
                </Button>
                <Button onClick={handleRun} disabled={!selectedSuite || !selectedAgent || submitting}>
                  {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Run Evaluation
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      <Tabs defaultValue="all" onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All ({displayRuns.length})</TabsTrigger>
          <TabsTrigger value="completed">Completed ({displayRuns.filter((r) => r.status === "completed").length})</TabsTrigger>
          <TabsTrigger value="running">Running ({displayRuns.filter((r) => r.status === "running").length})</TabsTrigger>
          <TabsTrigger value="failed">Failed ({displayRuns.filter((r) => r.status === "failed").length})</TabsTrigger>
        </TabsList>
        <TabsContent value={activeTab} className="mt-4">
          <Card>
            <CardContent className="p-0">
              {loading ? (
                <div className="p-4 space-y-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex items-center justify-between">
                      <div className="space-y-2">
                        <Skeleton className="h-4 w-40" />
                        <Skeleton className="h-3 w-24" />
                      </div>
                      <Skeleton className="h-6 w-20" />
                    </div>
                  ))}
                </div>
              ) : filtered.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                  <CheckCircle2 className="h-12 w-12 mb-4 text-emerald-500" />
                  <p className="text-lg font-medium">No {activeTab} evaluations</p>
                  <p className="text-sm">Run an evaluation suite to get started</p>
                </div>
              ) : (
                filtered.map((ev) => (
                  <div key={ev.id} className="flex items-center justify-between border-b p-4 last:border-0">
                    <div className="space-y-1">
                      <p className="text-sm font-medium">Run {ev.id.slice(0, 8)}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Clock className="h-3 w-3" />
                        {ev.started_at ? formatDate(ev.started_at) : "Pending"}
                        <span>&middot;</span>
                        <span>{ev.completed_sessions}/{ev.total_sessions} sessions</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {ev.aggregate_score !== null ? (
                        <span className={`text-sm font-semibold ${getScoreColor(ev.aggregate_score)}`}>
                          {formatScore(ev.aggregate_score)}
                        </span>
                      ) : (
                        <Progress value={ev.total_sessions > 0 ? (ev.completed_sessions / ev.total_sessions) * 100 : 0} className="w-16 h-2" />
                      )}
                      <Badge variant={ev.status === "completed" ? "success" : ev.status === "running" ? "warning" : "destructive"}>
                        {ev.status === "completed" && <CheckCircle2 className="mr-1 h-3 w-3" />}
                        {ev.status === "failed" && <XCircle className="mr-1 h-3 w-3" />}
                        {ev.status}
                      </Badge>
                      <Button variant="ghost" size="sm">
                        <Play className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
