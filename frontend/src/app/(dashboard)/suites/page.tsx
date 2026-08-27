"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/auth-context";
import { Layers, Plus, RefreshCw, Trash2, Loader2, X, CheckCircle2, FlaskConical } from "lucide-react";
import type { EvaluationSuite } from "@/types";

const API_BASE = "/api/v1";

function getHeaders() {
  const token = typeof window !== "undefined" ? localStorage.getItem("snt_auth_token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export default function SuitesPage() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const { data: suites, loading, refetch } = useApi(
    () => api.suites.list(orgId),
    [] as EvaluationSuite[],
  );

  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [success, setSuccess] = useState("");

  const [deleting, setDeleting] = useState<string | null>(null);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name) return;
    setSubmitting(true);
    setSubmitError("");
    setSuccess("");
    try {
      const res = await fetch(`${API_BASE}/suites`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({
          name,
          description: description || undefined,
          persona_config: [],
          chaos_profiles: {},
          judge_config: {},
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Failed to create suite" }));
        throw new Error(err.detail || "Failed to create suite");
      }
      setSuccess(`Suite "${name}" created`);
      setName(""); setDescription("");
      setShowCreate(false);
      refetch();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to create suite");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: string, suiteName: string) {
    if (!confirm(`Delete suite "${suiteName}"?`)) return;
    setDeleting(id);
    try {
      const res = await fetch(`${API_BASE}/suites/${id}`, {
        method: "DELETE",
        headers: getHeaders(),
      });
      if (!res.ok) throw new Error("Failed to delete suite");
      refetch();
    } catch {
      alert("Failed to delete suite");
    } finally {
      setDeleting(null);
    }
  }

  const personaCount = (suite: EvaluationSuite) => {
    if (Array.isArray(suite.persona_config)) return suite.persona_config.length;
    return 0;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Suites</h1>
          <p className="text-muted-foreground">Manage evaluation test suites</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={refetch}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="mr-2 h-4 w-4" /> New Suite
          </Button>
        </div>
      </div>

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-lg border bg-card p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">New Suite</h2>
              <Button variant="ghost" size="icon" onClick={() => setShowCreate(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name *</label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Red Team Suite v1" required />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Adversarial testing scenarios" />
              </div>
              <p className="text-xs text-muted-foreground">
                Personas, chaos profiles, and judge configuration can be added later when running evaluations.
              </p>
              {submitError && <p className="text-sm text-red-600">{submitError}</p>}
              {success && (
                <div className="flex items-center gap-2 text-sm text-emerald-600">
                  <CheckCircle2 className="h-4 w-4" /> {success}
                </div>
              )}
              <div className="flex justify-end gap-2 pt-2">
                <Button variant="outline" onClick={() => setShowCreate(false)} disabled={submitting}>Cancel</Button>
                <Button type="submit" disabled={!name || submitting}>
                  {submitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Create Suite
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">All Suites</CardTitle>
          <CardDescription>{(suites ?? []).length} suite{(suites ?? []).length !== 1 ? "s" : ""} configured</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          {loading ? (
            <div className="p-4 space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-3">
                  <Skeleton className="h-10 w-10 rounded-full" />
                  <div className="space-y-2 flex-1">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                  <Skeleton className="h-5 w-16" />
                </div>
              ))}
            </div>
          ) : (suites ?? []).length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Layers className="h-12 w-12 mb-4" />
              <p className="text-lg font-medium">No suites yet</p>
              <p className="text-sm">Create an evaluation suite to define test scenarios</p>
            </div>
          ) : (
            (suites ?? []).map((suite, i) => (
              <div key={suite.id}>
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <FlaskConical className="h-8 w-8 shrink-0 text-muted-foreground" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{suite.name}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{suite.description || "No description"}</span>
                        <span>&middot;</span>
                        <span>{personaCount(suite)} personas</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 ml-4">
                    <Badge variant={suite.is_active ? "default" : "secondary"}>
                      {suite.is_active ? "Active" : "Inactive"}
                    </Badge>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(suite.id, suite.name)} disabled={deleting === suite.id}>
                      {deleting === suite.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4 text-red-500" />}
                    </Button>
                  </div>
                </div>
                {i < (suites ?? []).length - 1 && <Separator />}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
