"use client";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { formatDate, formatScore } from "@/lib/utils";
import { useAuth } from "@/contexts/auth-context";
import type { RunMetadata } from "@/types";
import { AlertCircle, Inbox } from "lucide-react";

const statusColors: Record<string, string> = {
  completed: "success",
  running: "warning",
  failed: "destructive",
};

export function RecentRuns() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const { data: runs, loading, error } = useApi(
    () => api.evaluations.list(orgId),
    [] as RunMetadata[],
  );

  const displayRuns = (runs ?? []).slice(0, 5);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Recent Runs</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="flex items-center justify-between rounded-lg border p-3">
                <div className="space-y-2">
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-3 w-24" />
                </div>
                <Skeleton className="h-5 w-16" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground gap-2">
            <AlertCircle className="h-4 w-4 text-red-500" />
            Failed to load runs
          </div>
        ) : displayRuns.length === 0 ? (
          <div className="flex h-[200px] flex-col items-center justify-center text-muted-foreground">
            <Inbox className="h-8 w-8 mb-2" />
            <p className="text-sm">No evaluation runs yet</p>
          </div>
        ) : (
          <div className="space-y-3">
            {displayRuns.map((run) => (
              <div key={run.id} className="flex items-center justify-between rounded-lg border p-3">
                <div className="space-y-1">
                  <p className="text-sm font-medium leading-none">Run {run.id.slice(0, 8)}</p>
                  <p className="text-xs text-muted-foreground">
                    {run.completed_sessions}/{run.total_sessions} sessions &middot; {run.started_at ? formatDate(run.started_at) : "N/A"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  {run.aggregate_score !== null && (
                    <span className={`text-sm font-semibold ${run.aggregate_score >= 0.7 ? "text-emerald-600" : run.aggregate_score >= 0.5 ? "text-amber-600" : "text-red-600"}`}>
                      {formatScore(run.aggregate_score)}
                    </span>
                  )}
                  <Badge variant={(statusColors[run.status] || "secondary") as "success" | "warning" | "secondary" | "destructive"}>
                    {run.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
