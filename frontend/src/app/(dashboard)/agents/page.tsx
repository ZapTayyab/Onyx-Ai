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
import { Bot, Plus, RefreshCw, Trash2, Loader2, X, CheckCircle2 } from "lucide-react";
import type { TargetAgent } from "@/types";

const API_BASE = "/api/v1";

function getHeaders() {
  const token = typeof window !== "undefined" ? localStorage.getItem("snt_auth_token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export default function AgentsPage() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const { data: agents, loading, refetch } = useApi(
    () => api.agents.list(orgId),
    [] as TargetAgent[],
  );

  const [showCreate, setShowCreate] = useState(false);
  const [name, setName] = useState("");
  const [agentType, setAgentType] = useState("openai");
  const [modelName, setModelName] = useState("");
  const [endpointUrl, setEndpointUrl] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
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
      const res = await fetch(`${API_BASE}/agents`, {
        method: "POST",
        headers: getHeaders(),
        body: JSON.stringify({
          name,
          agent_type: agentType,
          model_name: modelName || undefined,
          endpoint_url: endpointUrl || undefined,
          system_prompt: systemPrompt || undefined,
          description: description || undefined,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Failed to create agent" }));
        throw new Error(err.detail || "Failed to create agent");
      }
      setSuccess(`Agent "${name}" created`);
      setName(""); setAgentType("openai"); setModelName(""); setEndpointUrl(""); setSystemPrompt(""); setDescription("");
      setShowCreate(false);
      refetch();
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to create agent");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: string, agentName: string) {
    if (!confirm(`Delete agent "${agentName}"?`)) return;
    setDeleting(id);
    try {
      const res = await fetch(`${API_BASE}/agents/${id}`, {
        method: "DELETE",
        headers: getHeaders(),
      });
      if (!res.ok) throw new Error("Failed to delete agent");
      refetch();
    } catch {
      alert("Failed to delete agent");
    } finally {
      setDeleting(null);
    }
  }

  const agentTypeColors: Record<string, "default" | "secondary" | "outline" | "destructive"> = {
    openai: "default", anthropic: "secondary", vllm: "outline", custom: "destructive",
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Agents</h1>
          <p className="text-muted-foreground">Manage target AI agents for evaluation</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={refetch}>
            <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} /> Refresh
          </Button>
          <Button onClick={() => setShowCreate(true)}>
            <Plus className="mr-2 h-4 w-4" /> New Agent
          </Button>
        </div>
      </div>

      {showCreate && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="w-full max-w-lg rounded-lg border bg-card p-6 shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">New Agent</h2>
              <Button variant="ghost" size="icon" onClick={() => setShowCreate(false)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Name *</label>
                <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="My Agent" required />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Agent Type</label>
                <select value={agentType} onChange={(e) => setAgentType(e.target.value)}
                  className="block w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring">
                  <option value="openai">OpenAI</option>
                  <option value="anthropic">Anthropic</option>
                  <option value="vllm">vLLM</option>
                  <option value="custom">Custom</option>
                </select>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Model Name</label>
                <Input value={modelName} onChange={(e) => setModelName(e.target.value)} placeholder="gpt-4o" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Endpoint URL</label>
                <Input value={endpointUrl} onChange={(e) => setEndpointUrl(e.target.value)} placeholder="https://api.openai.com/v1/chat/completions" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Description</label>
                <Input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional description" />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">System Prompt</label>
                <textarea value={systemPrompt} onChange={(e) => setSystemPrompt(e.target.value)} rows={3}
                  className="block w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  placeholder="You are a helpful assistant..." />
              </div>
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
                  Create Agent
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">All Agents</CardTitle>
          <CardDescription>{(agents ?? []).length} agent{(agents ?? []).length !== 1 ? "s" : ""} registered</CardDescription>
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
          ) : (agents ?? []).length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Bot className="h-12 w-12 mb-4" />
              <p className="text-lg font-medium">No agents yet</p>
              <p className="text-sm">Create an agent to get started with evaluations</p>
            </div>
          ) : (
            (agents ?? []).map((agent, i) => (
              <div key={agent.id}>
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <Bot className="h-8 w-8 shrink-0 text-muted-foreground" />
                    <div className="min-w-0">
                      <p className="text-sm font-medium truncate">{agent.name}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <span>{agent.model_name || "—"}</span>
                        <span>&middot;</span>
                        <span>v{agent.version || 1}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 ml-4">
                    <Badge variant={agentTypeColors[agent.agent_type] || "secondary"}>
                      {agent.agent_type}
                    </Badge>
                    <Button variant="ghost" size="icon" onClick={() => handleDelete(agent.id, agent.name)} disabled={deleting === agent.id}>
                      {deleting === agent.id ? <Loader2 className="h-4 w-4 animate-spin" /> : <Trash2 className="h-4 w-4 text-red-500" />}
                    </Button>
                  </div>
                </div>
                {i < (agents ?? []).length - 1 && <Separator />}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
