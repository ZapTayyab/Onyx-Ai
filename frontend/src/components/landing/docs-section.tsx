import { docsOverview } from "@/lib/landing-content";
import { BookOpen, Code, GitBranch, Shield, ArrowRight } from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
  BookOpen: <BookOpen className="h-5 w-5" />,
  Code: <Code className="h-5 w-5" />,
  GitBranch: <GitBranch className="h-5 w-5" />,
  Shield: <Shield className="h-5 w-5" />,
};

export function DocsSection() {
  return (
    <section id="docs" className="border-t border-slate-200 py-24 md:py-32 bg-white">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-600">
            {docsOverview.eyebrow}
          </p>
          <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            {docsOverview.headline}
          </h2>
        </div>
        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {docsOverview.categories.map((cat) => (
            <a
              key={cat.title}
              href="/docs"
              className="group rounded-xl border border-slate-200 bg-slate-50 p-6 transition-all hover:border-blue-200 hover:-translate-y-0.5 hover:shadow-sm"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-50 text-blue-600 transition-colors group-hover:bg-blue-100">
                {iconMap[cat.icon]}
              </div>
              <h3 className="mt-4 text-base font-semibold text-slate-900">{cat.title}</h3>
              <p className="mt-1 text-sm text-slate-500">{cat.count} articles</p>
            </a>
          ))}
        </div>
        <div className="mt-10 text-center">
          <a
            href="/docs"
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-5 text-sm font-medium text-slate-800 transition-all hover:bg-slate-50 hover:shadow-sm"
          >
            Browse all documentation
            <ArrowRight className="h-4 w-4" />
          </a>
        </div>
      </div>
    </section>
  );
}
