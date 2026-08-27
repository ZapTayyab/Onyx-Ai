"use client";

import { useState, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { formatDate, formatScore } from "@/lib/utils";
import { useAuth } from "@/contexts/auth-context";
import type { RunMetadata } from "@/types";
import { FileText, Download, Calendar, RefreshCw, AlertCircle, Inbox, CheckCircle2 } from "lucide-react";

export default function ReportsPage() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const [selectedFormat, setSelectedFormat] = useState("junit");
  const [generating, setGenerating] = useState(false);
  const [generated, setGenerated] = useState<string | null>(null);

  const { data: runs, loading, error, refetch } = useApi(
    () => api.evaluations.list(orgId),
    [] as RunMetadata[],
  );

  const reports = (runs ?? [])
    .filter((r) => r.status === "completed")
    .slice(0, 10)
    .map((r) => ({
      id: r.id,
      title: `Evaluation Report - ${r.id.slice(0, 8)}`,
      suite: `Run ${r.id.slice(0, 8)}`,
      created: r.completed_at || r.created_at,
      format: selectedFormat.toUpperCase(),
      score: r.aggregate_score,
    }));

  const handleGenerate = useCallback(async () => {
    if (!runs || runs.length === 0) return;
    setGenerating(true);
    setGenerated(null);
    try {
      const latest = runs.filter((r) => r.status === "completed")[0];
      if (!latest) {
        setGenerated("No completed runs to generate report for.");
        return;
      }
      const text = await api.evaluations.getReport(latest.id, selectedFormat as "summary" | "junit");
      const blob = new Blob([text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report-${latest.id.slice(0, 8)}.${selectedFormat === "junit" ? "xml" : "txt"}`;
      a.click();
      URL.revokeObjectURL(url);
      setGenerated("Report generated and downloaded successfully.");
    } catch {
      setGenerated("Failed to generate report.");
    } finally {
      setGenerating(false);
    }
  }, [runs, selectedFormat]);

  const handleDownloadReport = useCallback(async (runId: string) => {
    const run = runs?.find((r) => r.id === runId);
    if (!run) return;
    try {
      const text = await api.evaluations.getReport(run.id, selectedFormat as "summary" | "junit");
      const blob = new Blob([text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report-${run.id.slice(0, 8)}.${selectedFormat === "junit" ? "xml" : "txt"}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
    }
  }, [runs, selectedFormat]);

  return (
    <div className="space-y-6 max-w-3xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground">Generate and download evaluation reports</p>
        </div>
        <Button onClick={handleGenerate} disabled={generating || !runs?.length}>
          <FileText className="mr-2 h-4 w-4" /> {generating ? "Generating..." : "Generate Report"}
        </Button>
      </div>

      {generated && (
        <div className="flex items-center gap-2 rounded-md border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          {generated}
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Generate New Report</CardTitle>
          <CardDescription>Configure and generate a custom report</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label className="text-sm font-medium">Report Type</label>
              <div className="flex gap-2">
                {["junit", "summary", "pdf"].map((fmt) => (
                  <Button
                    key={fmt}
                    variant={selectedFormat === fmt ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedFormat(fmt)}
                  >
                    {fmt.toUpperCase()}
                  </Button>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Time Range</label>
              <div className="flex gap-2">
                {["7d", "30d", "90d"].map((range) => (
                  <Button key={range} variant="outline" size="sm">{range}</Button>
                ))}
              </div>
            </div>
          </div>
          <Button onClick={handleGenerate} disabled={generating || !runs?.length}>
            <RefreshCw className={`mr-2 h-4 w-4 ${generating ? "animate-spin" : ""}`} /> Generate
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Generated Reports</CardTitle>
          <CardDescription>Recently completed evaluation runs</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-4 space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center justify-between">
                  <div className="space-y-1">
                    <Skeleton className="h-4 w-48" />
                    <Skeleton className="h-3 w-32" />
                  </div>
                  <Skeleton className="h-5 w-16" />
                </div>
              ))}
            </div>
          ) : error ? (
            <div className="flex items-center justify-center gap-2 p-6 text-sm text-muted-foreground">
              <AlertCircle className="h-4 w-4 text-red-500" />
              Failed to load reports
            </div>
          ) : reports.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Inbox className="h-10 w-10 mb-3" />
              <p className="text-sm font-medium">No reports yet</p>
              <p className="text-xs">Completed evaluation runs will appear here</p>
            </div>
          ) : (
            reports.map((report, i) => (
              <div key={report.id}>
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-start gap-3">
                    <FileText className="h-5 w-5 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="text-sm font-medium">{report.title}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{report.suite}</span>
                        <span>·</span>
                        <Calendar className="h-3 w-3" />
                        {formatDate(report.created)}
                        {report.score !== null && (
                          <>
                            <span>·</span>
                            <span>Score: {formatScore(report.score)}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{report.format}</Badge>
                    <Button variant="ghost" size="icon" onClick={() => handleDownloadReport(report.id)}>
                      <Download className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
                {i < reports.length - 1 && <Separator />}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
