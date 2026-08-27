"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { useApi } from "@/hooks/use-api";
import { api } from "@/lib/api";
import { useAuth } from "@/contexts/auth-context";
import type { EvaluationSuite } from "@/types";
import { AlertCircle, Inbox } from "lucide-react";

interface PersonaItem {
  name: string;
  category: string;
}

function collectPersonas(suites: EvaluationSuite[]): PersonaItem[] {
  const seen = new Set<string>();
  const result: PersonaItem[] = [];
  for (const s of suites) {
    const configs = s.persona_config || [];
    for (const pc of configs) {
      const key = `${pc.name}-${pc.category}`;
      if (!seen.has(key)) {
        seen.add(key);
        result.push({ name: pc.name, category: pc.category || "standard" });
      }
    }
  }
  return result;
}

export function PersonaDistribution() {
  const { organization } = useAuth();
  const orgId = organization?.id || "";
  const { data: suites, loading, error } = useApi(
    () => api.suites.list(orgId),
    [] as EvaluationSuite[],
  );

  const personas = Array.isArray(suites) ? collectPersonas(suites) : [];

  const grouped = personas.reduce<Record<string, PersonaItem[]>>((acc, p) => {
    const cat = p.category;
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(p);
    return acc;
  }, {});

  const displayGroups = Object.entries(grouped).map(([category, items]) => ({
    category: category.charAt(0).toUpperCase() + category.slice(1).replace("_", " "),
    count: items.length,
  }));

  const totalPersonas = personas.length;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Persona Distribution</CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i}>
                <Skeleton className="h-5 w-20 mb-2" />
                <div className="space-y-2">
                  {[1, 2].map((j) => (
                    <div key={j} className="flex items-center gap-3">
                      <Skeleton className="h-4 w-24" />
                      <Skeleton className="h-2 flex-1" />
                      <Skeleton className="h-4 w-12" />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="flex h-[200px] items-center justify-center text-sm text-muted-foreground gap-2">
            <AlertCircle className="h-4 w-4 text-red-500" />
            Failed to load persona data
          </div>
        ) : totalPersonas === 0 ? (
          <div className="flex h-[200px] flex-col items-center justify-center text-muted-foreground">
            <Inbox className="h-8 w-8 mb-2" />
            <p className="text-sm">No personas configured</p>
          </div>
        ) : (
          <div className="space-y-4">
            {displayGroups.map((group) => {
              const pct = totalPersonas > 0 ? (group.count / totalPersonas) * 100 : 0;
              return (
                <div key={group.category}>
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant="outline" className="text-xs">{group.category}</Badge>
                  </div>
                  <div className="flex items-center gap-3">
                    <Progress value={pct} className="flex-1 h-2" />
                    <span className="text-sm text-muted-foreground w-12 text-right">{group.count}</span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
