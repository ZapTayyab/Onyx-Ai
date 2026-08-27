"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { useAuth } from "@/contexts/auth-context";
import { Bell, AlertTriangle, TrendingDown, Clock, CheckCircle2, Shield, Zap, RefreshCw } from "lucide-react";
import type { RunMetadata } from "@/types";

interface Alert {
  id: string;
  type: "score_regression" | "failure_spike" | "latency_increase" | "anomaly";
  severity: "critical" | "warning" | "info";
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

function buildAlerts(runs: RunMetadata[]): Alert[] {
  const alerts: Alert[] = [];
  const completed = runs.filter((r) => r.status === "completed" && r.aggregate_score != null);
  const sorted = [...completed].sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());

  for (let i = 1; i < sorted.length; i++) {
    const drop = (sorted[i - 1].aggregate_score ?? 0) - (sorted[i].aggregate_score ?? 0);
    if (drop > 0.15) {
      alerts.push({
        id: `reg-${sorted[i].id}`,
        type: "score_regression",
        severity: drop > 0.25 ? "critical" : "warning",
        message: `Score dropped ${(drop * 100).toFixed(0)}% in run ${sorted[i].id.slice(0, 8)} (${(sorted[i].aggregate_score! * 100).toFixed(0)}%)`,
        timestamp: sorted[i].created_at,
        acknowledged: false,
      });
    }
  }

  const failed = runs.filter((r) => r.status === "failed");
  if (failed.length > 2) {
    alerts.push({
      id: "fail-spike",
      type: "failure_spike",
      severity: "warning",
      message: `${failed.length} failed runs detected`,
      timestamp: new Date().toISOString(),
      acknowledged: false,
    });
  }

  return alerts.slice(0, 10);
}

const severityColors: Record<string, "destructive" | "warning" | "secondary"> = {
  critical: "destructive", warning: "warning", info: "secondary",
};

const typeIcons: Record<string, React.ReactNode> = {
  score_regression: <TrendingDown className="h-4 w-4" />,
  failure_spike: <AlertTriangle className="h-4 w-4" />,
  latency_increase: <Clock className="h-4 w-4" />,
  anomaly: <Zap className="h-4 w-4" />,
};

export default function AlertsPage() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const [activeTab, setActiveTab] = useState("all");
  const [acknowledged, setAcknowledged] = useState<Set<string>>(new Set());

  const { data: runs, loading } = useApi(() => api.evaluations.list(orgId), [] as RunMetadata[]);

  const alerts = runs && runs.length > 0 ? buildAlerts(runs) : [];

  const filtered = activeTab === "all"
    ? alerts
    : activeTab === "unacknowledged"
      ? alerts.filter((a) => !acknowledged.has(a.id))
      : alerts.filter((a) => a.severity === activeTab);

  const acknowledge = (id: string) => {
    setAcknowledged(new Set(acknowledged).add(id));
  };

  const unacknowledgedCount = alerts.filter((a) => !acknowledged.has(a.id)).length;

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Alerts</h1>
          <p className="text-muted-foreground">
            {unacknowledgedCount > 0 ? `${unacknowledgedCount} unacknowledged` : "No unacknowledged alerts"}
          </p>
        </div>
        <Button variant="outline" size="sm">
          <Bell className="mr-2 h-4 w-4" /> Configure
        </Button>
      </div>

      <Tabs defaultValue="all" onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all">All ({alerts.length})</TabsTrigger>
          <TabsTrigger value="unacknowledged">
            Unacknowledged
            {unacknowledgedCount > 0 && (
              <Badge variant="destructive" className="ml-2 text-[10px] px-1">{unacknowledgedCount}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="critical">Critical</TabsTrigger>
          <TabsTrigger value="warning">Warning</TabsTrigger>
        </TabsList>
        <TabsContent value={activeTab} className="mt-4 space-y-3">
          {loading ? (
            [1, 2, 3].map((i) => (
              <Card key={i}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Skeleton className="h-4 w-4 rounded" />
                    <div className="flex-1 space-y-2">
                      <Skeleton className="h-4 w-3/4" />
                      <Skeleton className="h-3 w-1/4" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          ) : filtered.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                <CheckCircle2 className="h-12 w-12 mb-4 text-emerald-500" />
                <p className="text-lg font-medium">All clear</p>
                <p className="text-sm">No alerts in this category</p>
              </CardContent>
            </Card>
          ) : (
            filtered.map((alert) => (
              <Card key={alert.id} className={!acknowledged.has(alert.id) ? "border-l-4 border-l-primary" : ""}>
                <CardContent className="p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <div className={`mt-0.5 ${alert.severity === "critical" ? "text-red-500" : alert.severity === "warning" ? "text-amber-500" : "text-blue-500"}`}>
                        {typeIcons[alert.type]}
                      </div>
                      <div>
                        <p className="text-sm font-medium">{alert.message}</p>
                        <p className="text-xs text-muted-foreground mt-1">{formatDate(alert.timestamp)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <Badge variant={severityColors[alert.severity]}>{alert.severity}</Badge>
                      {!acknowledged.has(alert.id) && (
                        <Button variant="ghost" size="sm" className="text-xs" onClick={() => acknowledge(alert.id)}>
                          <CheckCircle2 className="mr-1 h-3 w-3" /> Acknowledge
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
