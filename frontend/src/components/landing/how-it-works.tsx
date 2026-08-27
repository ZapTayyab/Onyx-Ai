"use client";

import { useRef } from "react";
import { cn } from "@/lib/utils";
import { Reveal } from "./reveal";
import { pipelineSteps } from "@/lib/landing-content";
import type { Phase } from "@/lib/landing-content";
import {
  Users, Play, Activity, Scale, TrendingDown, FileText, Clock,
} from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
  Users: <Users className="h-6 w-6" />,
  Play: <Play className="h-6 w-6" />,
  Activity: <Activity className="h-6 w-6" />,
  Scale: <Scale className="h-6 w-6" />,
  TrendingDown: <TrendingDown className="h-6 w-6" />,
  FileText: <FileText className="h-6 w-6" />,
};

const phaseConfig: Record<Phase, { dot: string; rail: string; border: string; bg: string; ring: string; badge: string; label: string; text: string }> = {
  generation: {
    dot: "bg-indigo-500 border-indigo-400",
    rail: "bg-indigo-500",
    border: "border-indigo-200",
    bg: "bg-indigo-50",
    ring: "ring-indigo-100",
    badge: "bg-indigo-500",
    label: "text-indigo-600",
    text: "text-indigo-700",
  },
  execution: {
    dot: "bg-cyan-500 border-cyan-400",
    rail: "bg-cyan-500",
    border: "border-cyan-200",
    bg: "bg-cyan-50",
    ring: "ring-cyan-100",
    badge: "bg-cyan-500",
    label: "text-cyan-600",
    text: "text-cyan-700",
  },
  output: {
    dot: "bg-emerald-500 border-emerald-400",
    rail: "bg-emerald-500",
    border: "border-emerald-200",
    bg: "bg-emerald-50",
    ring: "ring-emerald-100",
    badge: "bg-emerald-500",
    label: "text-emerald-600",
    text: "text-emerald-700",
  },
};

const phaseOrder: Phase[] = ["generation", "execution", "output"];
const phaseLabels: Record<Phase, string> = {
  generation: "Generation",
  execution: "Execution",
  output: "Output",
};

export function HowItWorks() {
  const sectionRef = useRef<HTMLElement>(null);

  return (
    <section
      ref={sectionRef}
      id="how-it-works"
      className="border-t border-slate-200 py-24 md:py-32 bg-white overflow-hidden"
    >
      <div className="mx-auto max-w-7xl px-6">
        <Reveal>
          <div className="mx-auto max-w-2xl text-center">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
              The engine
            </p>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              From scenario to report. A repeatable, six-stage pipeline.
            </h2>
            <p className="mt-4 text-base leading-relaxed text-slate-600">
              Every evaluation follows the same deterministic path — from persona synthesis to auditable output.
            </p>
          </div>
        </Reveal>

        {/* Desktop pipeline */}
        <div className="mt-20 hidden lg:block">
          {/* Phase labels */}
          <div className="flex mb-6">
            {phaseOrder.map((phase, pi) => {
              const count = pipelineSteps.filter((s) => s.phase === phase).length;
              const cfg = phaseConfig[phase];
              return (
                <div
                  key={phase}
                  className="flex-1 flex items-center gap-2"
                  style={{ flex: count }}
                >
                  <span className={cn("inline-flex h-5 items-center rounded-full px-2.5 text-[10px] font-bold uppercase tracking-wider text-white", cfg.badge)}>
                    {phaseLabels[phase]}
                  </span>
                  {pi < phaseOrder.length - 1 && (
                    <div className="flex-1 h-px bg-slate-200" />
                  )}
                </div>
              );
            })}
          </div>

          <div className="grid grid-cols-3 grid-rows-2 gap-4 pipeline-grid">
            {pipelineSteps.map((step, i) => {
              const cfg = phaseConfig[step.phase];
              return (
                <Reveal key={step.number} delay={i * 80} className="z-10">
                  <div
                    className={cn(
                      "group relative rounded-2xl border-2 p-6 transition-all duration-500",
                      "hover:-translate-y-1 hover:shadow-lg",
                      cfg.bg,
                      cfg.border,
                    )}
                  >
                    <div className="flex flex-col h-full">
                      <div className="flex items-center justify-between mb-4">
                        <div
                          className={cn(
                            "flex h-11 w-11 items-center justify-center rounded-xl ring-4 transition-all duration-500 group-hover:scale-110",
                            cfg.ring,
                            cfg.dot,
                          )}
                        >
                          <span className="text-white">
                            {iconMap[step.icon]}
                          </span>
                        </div>
                        <span className={cn("text-[10px] font-bold tracking-wider uppercase", cfg.label)}>
                          {step.phase}
                        </span>
                      </div>

                      <div className="flex items-center gap-1.5 mb-2">
                        <span className={cn("text-xs font-bold", cfg.label)}>
                          {step.number}
                        </span>
                        <h3 className="text-base font-bold text-slate-900 leading-snug">
                          {step.title}
                        </h3>
                      </div>

                      <p className="text-xs leading-relaxed text-slate-600 flex-1">
                        {step.description}
                      </p>

                      {step.duration && (
                        <div className="mt-auto pt-4 flex items-center gap-1.5 text-xs font-semibold text-indigo-600 bg-indigo-50/80 rounded-md px-2.5 py-1 w-fit">
                          <Clock className="h-3.5 w-3.5" />
                          {step.duration}
                        </div>
                      )}
                    </div>
                  </div>
                </Reveal>
              );
            })}
          </div>
        </div>

        {/* Mobile vertical timeline */}
        <div className="mt-16 lg:hidden space-y-10">
          {pipelineSteps.map((step, i) => {
            const cfg = phaseConfig[step.phase];
            return (
              <Reveal key={step.number} delay={i * 80}>
                <div className="relative flex gap-5">
                  {/* Timeline column */}
                  <div className="flex flex-col items-center">
                    <div
                      className={cn(
                        "relative z-10 flex h-11 w-11 items-center justify-center rounded-xl ring-4 transition-all",
                        cfg.ring,
                        cfg.dot,
                      )}
                    >
                      <span className="text-white">
                        {iconMap[step.icon]}
                      </span>
                    </div>
                    {i < pipelineSteps.length - 1 && (
                      <div className="mt-1 w-0.5 flex-1 bg-slate-200 rounded-full" />
                    )}
                  </div>

                  {/* Card */}
                  <div className={cn("flex-1 rounded-xl border-2 p-5 mb-2", cfg.bg, cfg.border)}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className={cn("text-xs font-bold", cfg.label)}>
                        {step.number}
                      </span>
                      <span className={cn("inline-flex h-4 items-center rounded-full px-2 text-[9px] font-bold uppercase tracking-wider text-white", cfg.badge)}>
                        {phaseLabels[step.phase]}
                      </span>
                    </div>
                    <h3 className="text-base font-bold text-slate-900">{step.title}</h3>
                    <p className="mt-1.5 text-sm leading-relaxed text-slate-600">{step.description}</p>
                    {step.duration && (
                      <div className="mt-3 flex items-center gap-1.5 text-xs font-medium text-slate-400">
                        <Clock className="h-3 w-3" />
                        {step.duration}
                      </div>
                    )}
                  </div>
                </div>
              </Reveal>
            );
          })}
        </div>

        <Reveal delay={500}>
          <div className="relative mt-16 text-center">
            <div className="inline-flex items-center gap-3 rounded-full border border-slate-200 bg-slate-50 px-5 py-2 text-sm text-slate-600">
              <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              End-to-end in under 5 minutes
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
