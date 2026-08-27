import { MetricCards, ScoreChart, CategoryChart } from "@/components/dashboard/metric-cards";
import { RecentRuns } from "@/components/dashboard/recent-runs";
import { PersonaDistribution } from "@/components/dashboard/persona-distribution";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Overview of your AI agent evaluation metrics
        </p>
      </div>
      <MetricCards />
      <div className="grid gap-4 md:grid-cols-3">
        <ScoreChart />
        <CategoryChart />
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <RecentRuns />
        <PersonaDistribution />
      </div>
    </div>
  );
}
