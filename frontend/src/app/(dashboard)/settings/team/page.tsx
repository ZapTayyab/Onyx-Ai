"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/auth-context";
import { UserPlus, Shield, Mail, RefreshCw, CheckCircle2 } from "lucide-react";
import type { MemberResponse } from "@/types";

const roleColors: Record<string, "default" | "secondary" | "outline"> = {
  admin: "default", member: "secondary", viewer: "outline",
};

export default function TeamPage() {
  const { organization } = useAuth();
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviting, setInviting] = useState(false);
  const [inviteSuccess, setInviteSuccess] = useState("");
  const [inviteError, setInviteError] = useState("");

  const { data: members, loading, refetch } = useApi(
    () => api.org.members(),
    [] as MemberResponse[],
  );

  const activeMembers = (members ?? []).filter((m) => m.is_active);

  const handleInvite = async () => {
    if (!inviteEmail) return;
    setInviting(true);
    setInviteSuccess("");
    setInviteError("");
    try {
      const API_BASE = "/api/v1";
      const res = await fetch(
        `${API_BASE}/organizations/me/invite`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(localStorage.getItem("snt_auth_token")
              ? { Authorization: `Bearer ${localStorage.getItem("snt_auth_token")}` }
              : {}),
          },
          body: JSON.stringify({ email: inviteEmail, role: "member" }),
        },
      );
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Invite failed" }));
        throw new Error(err.detail || "Failed to send invite");
      }
      setInviteSuccess(`Invitation sent to ${inviteEmail}`);
      setInviteEmail("");
      refetch();
    } catch (err) {
      setInviteError(err instanceof Error ? err.message : "Failed to send invite");
    } finally {
      setInviting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Team</h1>
          <p className="text-muted-foreground">{activeMembers.length} active members</p>
        </div>
        <Button variant="outline" size="sm" onClick={refetch}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} /> Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Invite Member</CardTitle>
          <CardDescription>Send an invitation to join your organization</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex gap-2">
            <Input placeholder="colleague@company.com" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} className="flex-1" />
            <Button onClick={handleInvite} disabled={inviting || !inviteEmail}>
              <UserPlus className="mr-2 h-4 w-4" /> {inviting ? "Inviting..." : "Invite"}
            </Button>
          </div>
          {inviteSuccess && (
            <div className="flex items-center gap-2 text-sm text-emerald-600">
              <CheckCircle2 className="h-4 w-4" /> {inviteSuccess}
            </div>
          )}
          {inviteError && (
            <p className="text-sm text-red-600">{inviteError}</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Members ({activeMembers.length})</CardTitle>
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
          ) : (
            activeMembers.map((member, i) => (
              <div key={member.id}>
                <div className="flex items-center justify-between p-4">
                  <div className="flex items-center gap-3">
                    <Avatar className="h-10 w-10">
                      <AvatarFallback>{member.email.slice(0, 2).toUpperCase()}</AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="text-sm font-medium">{member.email.split("@")[0]}</p>
                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                        <Mail className="h-3 w-3" /> {member.email}
                      </div>
                    </div>
                  </div>
                  <Badge variant={roleColors[member.role] || "secondary"}>
                    {member.role === "admin" && <Shield className="mr-1 h-3 w-3" />}
                    {member.role}
                  </Badge>
                </div>
                {i < activeMembers.length - 1 && <Separator />}
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
