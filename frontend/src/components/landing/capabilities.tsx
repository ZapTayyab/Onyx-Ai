import { Reveal } from "./reveal";
import { capabilities } from "@/lib/landing-content";
import {
  UserCheck, Zap, Scale, TrendingDown, GitBranch, FileText,
} from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
  UserCheck: <UserCheck className="h-6 w-6" />,
  Zap: <Zap className="h-6 w-6" />,
  Scale: <Scale className="h-6 w-6" />,
  TrendingDown: <TrendingDown className="h-6 w-6" />,
  GitBranch: <GitBranch className="h-6 w-6" />,
  FileText: <FileText className="h-6 w-6" />,
};

const featured = capabilities.filter((c) => c.featured);
const regular = capabilities.filter((c) => !c.featured);

function CapabilityCard({ cap, index }: { cap: (typeof capabilities)[number]; index: number }) {
  return (
    <Reveal delay={index * 100}>
      <div className="group relative rounded-2xl border border-slate-200 bg-white p-6 md:p-7 transition-all duration-500 hover:border-indigo-300 hover:shadow-[0_0_30px_-8px] hover:shadow-indigo-200/50 hover:-translate-y-0.5 h-full flex flex-col">
        <div className="flex items-start gap-4">
          <div
              className="flex h-12 w-12 shrink-0 items-center justify-center transition-all duration-500 group-hover:scale-110"
              style={{ background: "rgba(99, 102, 241, 0.1)", borderRadius: "50%" }}
            >
              <span className="text-indigo-600 group-hover:text-indigo-500 transition-colors duration-500">
                {iconMap[cap.icon]}
              </span>
          </div>
          <div className="min-w-0 flex-1">
            <h3 className="text-base font-bold text-slate-900">
              {cap.title}
            </h3>
            <p className="mt-1.5 text-sm leading-relaxed text-slate-600">
              {cap.description}
            </p>
          </div>
        </div>

        <div className="mt-auto pt-5 flex items-baseline gap-2.5 border-t border-slate-100">
          <span className="font-mono text-xl font-bold text-indigo-600 transition-all duration-300 group-hover:scale-105 group-hover:text-indigo-500 inline-block">
            {cap.metric.value}
          </span>
          <span className="text-xs text-slate-500 font-medium">
            {cap.metric.label}
          </span>
        </div>

        <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-50/0 to-indigo-50/0 transition-all duration-500 group-hover:from-indigo-50/40 group-hover:to-indigo-50/20" />
      </div>
    </Reveal>
  );
}

function FeaturedCard({ cap, index }: { cap: (typeof capabilities)[number]; index: number }) {
  return (
    <Reveal delay={index * 100}>
      <div className="group relative rounded-2xl border border-slate-200 bg-white p-7 md:p-8 transition-all duration-500 hover:border-indigo-300 hover:shadow-[0_0_40px_-12px] hover:shadow-indigo-200/50 hover:-translate-y-0.5 h-full flex flex-col">
        <div className="flex items-start gap-4">
          <div
              className="flex h-14 w-14 shrink-0 items-center justify-center transition-all duration-500 group-hover:scale-110"
              style={{ background: "rgba(99, 102, 241, 0.1)", borderRadius: "50%" }}
            >
              <span className="text-indigo-600 group-hover:text-indigo-500 transition-colors duration-500">
                {iconMap[cap.icon]}
              </span>
          </div>
          <div className="min-w-0 flex-1">
            <div className="inline-flex items-center gap-1.5 rounded-full bg-indigo-50 px-2.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-indigo-600 mb-2">
              <span className="h-1.5 w-1.5 rounded-full bg-indigo-500" />
              Headline capability
            </div>
            <h3 className="text-xl font-bold text-slate-900">
              {cap.title}
            </h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-600">
              {cap.description}
            </p>
          </div>
        </div>

        <div className="relative mt-6 mb-5 h-2 rounded-full bg-slate-100 overflow-hidden">
          <div className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-indigo-400 to-indigo-600 transition-all duration-1000 group-hover:from-indigo-500 group-hover:to-violet-500" style={{ width: `${Math.random() * 30 + 65}%` }} />
        </div>

        <div className="mt-auto pt-5 flex items-baseline gap-2.5 border-t border-slate-100">
          <span className="font-mono text-2xl font-bold text-indigo-600 transition-all duration-300 group-hover:scale-105 group-hover:text-indigo-500 inline-block">
            {cap.metric.value}
          </span>
          <span className="text-sm text-slate-500 font-medium">
            {cap.metric.label}
          </span>
        </div>

        <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-50/0 to-indigo-50/0 transition-all duration-500 group-hover:from-indigo-50/40 group-hover:to-indigo-50/20" />
      </div>
    </Reveal>
  );
}

export function Capabilities() {
  return (
    <section id="capabilities" className="border-t border-slate-200 py-24 md:py-32 bg-slate-50">
      <div className="mx-auto max-w-7xl px-6">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
              Enterprise capabilities
            </p>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Everything you need to assure AI agents at scale.
            </h2>
          </div>
        </Reveal>

        <div className="mt-16 space-y-6">
          {/* Featured row: Synthetic Personas + Chaos Injection */}
          <div className="grid gap-6 lg:grid-cols-5">
            <div className="lg:col-span-3">
              <FeaturedCard cap={featured[0]} index={0} />
            </div>
            <div className="lg:col-span-2">
              <FeaturedCard cap={featured[1]} index={1} />
            </div>
          </div>

          {/* Regular 2×2 grid */}
          <div className="grid gap-6 sm:grid-cols-2">
            {regular.map((cap, i) => (
              <CapabilityCard key={cap.title} cap={cap} index={i + 2} />
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
