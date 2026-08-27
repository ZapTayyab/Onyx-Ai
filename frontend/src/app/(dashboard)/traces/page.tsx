"use client";

import { useState } from "react";
import {
  Card, CardContent, CardHeader, CardTitle, CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { formatScore, getScoreColor, cn } from "@/lib/utils";
import { useAuth } from "@/contexts/auth-context";
import { Play, Pause, AlertCircle, Inbox, Shield, MessageSquare, AlertTriangle, Zap, Layers, ChevronRight } from "lucide-react";
import type { RunMetadata, TurnTrace, TraceQueryResponse } from "@/types";

interface GroupedTrace {
  session_id: string;
  persona_name: string;
  turns: TurnTrace[];
  avgScore: number;
}

function groupTraces(turns: TurnTrace[]): GroupedTrace[] {
  const map = new Map<string, TurnTrace[]>();
  for (const t of turns) {
    const sid = t.session_id;
    if (!map.has(sid)) map.set(sid, []);
    map.get(sid)!.push(t);
  }
  const result: GroupedTrace[] = [];
  Array.from(map.entries()).forEach(([session_id, sessionTurns]) => {
    const scores = sessionTurns
      .filter((t) => t.scores?.overall != null)
      .map((t) => t.scores.overall);
    const avgScore = scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0;
    const personaName = sessionTurns[0]?.metadata?.persona_name as string || sessionTurns[0]?.session_id?.split("-").slice(1).join("-") || session_id;
    result.push({ session_id, persona_name: personaName, turns: sessionTurns, avgScore });
  });
  return result.sort((a, b) => b.avgScore - a.avgScore);
}

const categoryIcons: Record<string, React.ReactNode> = {
  standard: <MessageSquare className="h-4 w-4 text-blue-500" />,
  adversarial: <Shield className="h-4 w-4 text-red-500" />,
  edge_case: <AlertTriangle className="h-4 w-4 text-amber-500" />,
};

const categoryColors: Record<string, string> = {
  standard: "bg-blue-50 border-blue-200",
  adversarial: "bg-red-50 border-red-200",
  edge_case: "bg-amber-50 border-amber-200",
};

function inferCategory(name: string): string {
  const l = name.toLowerCase();
  if (l.includes("jailbreak") || l.includes("adversarial") || l.includes("data")) return "adversarial";
  if (l.includes("confused") || l.includes("edge") || l.includes("rapid") || l.includes("non")) return "edge_case";
  return "standard";
}

function TurnMessage({ trace, index }: { trace: TurnTrace; index: number }) {
  const isUser = trace.speaker === "user";
  const score = trace.scores?.overall;
  const issues = Object.keys(trace.chaos_injected || {}).filter((k) => trace.chaos_injected[k]);

  return (
    <div className={cn("flex gap-3", isUser ? "" : "flex-row-reverse")}>
      <div className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold",
        isUser ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
      )}>
        {isUser ? "U" : "A"}
      </div>
      <div className={cn("flex-1 rounded-lg border p-3 text-sm", isUser ? "bg-primary/5" : "bg-muted/50")}>
        <p className="leading-relaxed">{trace.turn_text}</p>
        {score !== undefined && (
          <div className="mt-2 flex items-center gap-2">
            <Zap className={cn("h-3 w-3", getScoreColor(score))} />
            <span className={cn("text-xs font-medium", getScoreColor(score))}>Score: {formatScore(score)}</span>
          </div>
        )}
        {issues.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {issues.map((issue) => (
              <Badge key={issue} variant="destructive" className="text-[10px] px-1.5 py-0">{issue}</Badge>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default function TracesPage() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [isAnimating, setIsAnimating] = useState(false);

  const { data: runs, loading: runsLoading, error: runsError } = useApi(
    () => api.evaluations.list(orgId),
    [] as RunMetadata[],
  );

  const { data: traceResp, loading: tracesLoading, error: tracesError } = useApi<
    TraceQueryResponse
  >(
    () => selectedRunId
      ? api.evaluations.getTraces(orgId, selectedRunId) as Promise<TraceQueryResponse>
      : Promise.resolve({ turns: [], total: 0 }),
    { turns: [], total: 0 },
    [selectedRunId],
  );

  const traces = traceResp?.turns ?? [];
  const grouped = groupTraces(traces);
  const [selectedSession, setSelectedSession] = useState(grouped[0]?.session_id || "");
  const currentGroup = grouped.find((g) => g.session_id === selectedSession) || grouped[0];

  if (runsError) {
    return (
      <div className="flex h-[400px] items-center justify-center gap-2 text-red-600">
        <AlertCircle className="h-5 w-5" />
        Failed to load runs: {runsError}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Trace Viewer</h1>
          <p className="text-muted-foreground">Multi-turn conversation tracing and turn-by-turn analysis</p>
        </div>
        <div className="flex items-center gap-2">
          {currentGroup && (
            <Button variant="outline" size="sm" onClick={() => setIsAnimating(!isAnimating)}>
              {isAnimating ? <><Pause className="mr-2 h-4 w-4" /> Pause</> : <><Play className="mr-2 h-4 w-4" /> Play Turns</>}
            </Button>
          )}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Sessions</CardTitle>
            <CardDescription>
              {selectedRunId
                ? `${grouped.length} sessions`
                : "Select a run to view traces"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-2 p-2">
            {!selectedRunId ? (
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground px-2 mb-2">Choose a run:</p>
                {runsLoading ? (
                  [1, 2, 3].map((i) => (
                    <div key={i} className="rounded-lg border p-3">
                      <Skeleton className="h-4 w-24 mb-1" />
                      <Skeleton className="h-3 w-16" />
                    </div>
                  ))
                ) : runs && runs.length > 0 ? (
                  runs.slice(0, 10).map((run) => (
                    <button
                      key={run.id}
                      onClick={() => {
                        setSelectedRunId(run.id);
                        setSelectedSession("");
                      }}
                      className={cn(
                        "w-full rounded-lg border p-3 text-left transition-colors hover:bg-accent",
                        selectedRunId === run.id ? "border-primary bg-primary/5" : ""
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium truncate">Run {run.id.slice(0, 8)}</span>
                        <ChevronRight className="h-4 w-4 text-muted-foreground" />
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {run.status} &middot; {run.completed_sessions}/{run.total_sessions} sessions
                      </div>
                    </button>
                  ))
                ) : (
                  <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                    <Inbox className="h-8 w-8 mb-2" />
                    <p className="text-sm">No runs available</p>
                  </div>
                )}
              </div>
            ) : tracesLoading ? (
              [1, 2, 3].map((i) => (
                <div key={i} className="rounded-lg border p-3">
                  <Skeleton className="h-4 w-24 mb-2" />
                  <Skeleton className="h-3 w-16" />
                </div>
              ))
            ) : tracesError ? (
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <AlertCircle className="h-8 w-8 mb-2 text-red-500" />
                <p className="text-sm">Failed to load traces</p>
              </div>
            ) : grouped.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-muted-foreground">
                <Inbox className="h-8 w-8 mb-2" />
                <p className="text-sm">No trace data for this run</p>
              </div>
            ) : (
              <>
                <button
                  onClick={() => { setSelectedRunId(null); setSelectedSession(""); }}
                  className="w-full text-left text-xs text-muted-foreground hover:text-foreground mb-2 px-2"
                >
                  &larr; Back to runs
                </button>
                {grouped.map((session) => {
                  const cat = inferCategory(session.persona_name);
                  return (
                    <button
                      key={session.session_id}
                      onClick={() => setSelectedSession(session.session_id)}
                      className={cn(
                        "w-full rounded-lg border p-3 text-left transition-colors hover:bg-accent",
                        currentGroup?.session_id === session.session_id ? "border-primary bg-primary/5" : categoryColors[cat]
                      )}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <div className="flex items-center gap-2">
                          {categoryIcons[cat]}
                          <span className="text-sm font-medium truncate">{session.persona_name}</span>
                        </div>
                        <Badge variant="outline" className="text-[10px]">{cat}</Badge>
                      </div>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>{session.turns.length} turns</span>
                        <span className={getScoreColor(session.avgScore)}>{formatScore(session.avgScore)}</span>
                      </div>
                    </button>
                  );
                })}
              </>
            )}
          </CardContent>
        </Card>

        <Card>
          {currentGroup && selectedRunId ? (
            <>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle className="text-base">{currentGroup.persona_name}</CardTitle>
                    <CardDescription>
                      {currentGroup.turns.length} turns &middot; Avg Score: {formatScore(currentGroup.avgScore)}
                    </CardDescription>
                  </div>
                  <Badge variant={currentGroup.avgScore >= 0.8 ? "success" : "warning"}>
                    {currentGroup.avgScore >= 0.8 ? "PASS" : "REVIEW"}
                  </Badge>
                </div>
                <Separator />
              </CardHeader>
              <CardContent className="space-y-4">
                {currentGroup.turns
                  .sort((a, b) => a.turn_id - b.turn_id)
                  .map((trace, idx) => (
                    <TurnMessage key={idx} trace={trace} index={idx} />
                  ))}
              </CardContent>
            </>
          ) : (
            <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Layers className="h-12 w-12 mb-4" />
              <p className="text-lg font-medium">Select a run</p>
              <p className="text-sm">Choose a run from the sidebar to view its trace data</p>
            </CardContent>
          )}
        </Card>
      </div>
    </div>
  );
}
