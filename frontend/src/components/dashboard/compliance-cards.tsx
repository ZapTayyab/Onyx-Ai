"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ShieldAlert, CheckCircle } from "lucide-react";

export function AgenticRiskCard({
  riskScore = 92.5,
  totalInteractions = 45,
  blockedAttacks = 42,
  loading = false,
}: {
  riskScore?: number;
  totalInteractions?: number;
  blockedAttacks?: number;
  loading?: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Agentic Risk Score
        </CardTitle>
        <ShieldAlert className="h-4 w-4 text-amber-500" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-24 mb-1" />
        ) : (
          <div className="text-2xl font-bold text-emerald-500">{riskScore}%</div>
        )}
        <p className="text-xs text-muted-foreground">
          {blockedAttacks}/{totalInteractions} tool-calling attack vectors blocked
        </p>
      </CardContent>
    </Card>
  );
}

export function ComplianceCoverageCard({
  coverageRate = 100,
  standardsCount = 18,
  loading = false,
}: {
  coverageRate?: number;
  standardsCount?: number;
  loading?: boolean;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          Compliance Coverage
        </CardTitle>
        <CheckCircle className="h-4 w-4 text-emerald-500" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-24 mb-1" />
        ) : (
          <div className="text-2xl font-bold">{coverageRate}%</div>
        )}
        <p className="text-xs text-muted-foreground">
          {standardsCount} OWASP / NIST standards actively tested
        </p>
      </CardContent>
    </Card>
  );
}
