import { Reveal } from "./reveal";
import { cta } from "@/lib/landing-content";
import { ArrowRight, Shield, Check } from "lucide-react";

export function CTASection() {
  return (
    <section className="relative overflow-hidden bg-indigo-950 py-24 md:py-32">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(99,102,241,0.15),transparent_70%)]" />
      <div className="pointer-events-none absolute -top-40 right-0 h-80 w-80 rounded-full bg-indigo-500/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-violet-500/10 blur-3xl" />

      <div className="relative mx-auto max-w-4xl px-6 text-center">
        <Reveal>
          <div className="inline-flex items-center gap-2 rounded-full border border-indigo-700/50 bg-indigo-900/50 px-4 py-1.5 text-xs font-medium text-indigo-300 mb-6 backdrop-blur-sm">
            <Shield className="h-3.5 w-3.5" />
            Get started
          </div>

          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl lg:text-5xl leading-tight">
            {cta.headline}
          </h2>

          <p className="mt-4 text-lg leading-relaxed text-indigo-200 max-w-xl mx-auto">
            {cta.subheadline}
          </p>

          <div className="mt-10 flex flex-wrap justify-center gap-4">
            <a
              href={cta.primary.href}
              className="inline-flex h-12 items-center justify-center gap-2 rounded-lg bg-white px-7 text-sm font-semibold text-indigo-950 transition-all hover:bg-indigo-50 hover:shadow-[0_0_30px_-8px] hover:shadow-white/30"
            >
              {cta.primary.label}
              <ArrowRight className="h-4 w-4" />
            </a>
            <a
              href={cta.secondary.href}
              className="inline-flex h-12 items-center justify-center rounded-lg border border-indigo-500/40 bg-indigo-900/30 px-7 text-sm font-semibold text-indigo-100 transition-all hover:bg-indigo-800/50 hover:border-indigo-400/60 backdrop-blur-sm"
            >
              {cta.secondary.label}
            </a>
          </div>

          {/* 3-step expectation strip */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-x-3 gap-y-2 text-sm">
            {cta.steps.map((step, i) => (
              <div key={step} className="flex items-center gap-2">
                <span className="font-mono text-xs text-indigo-400 font-bold">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <span className="text-indigo-200">{step}</span>
                {i < cta.steps.length - 1 && (
                  <ArrowRight className="h-3.5 w-3.5 text-indigo-600" />
                )}
              </div>
            ))}
          </div>

          {/* Micro-trust line */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-1 text-xs text-indigo-400/70">
            {cta.trustLine.split(" · ").map((item) => (
              <span key={item} className="flex items-center gap-1.5">
                <Check className="h-3 w-3 text-indigo-500" />
                {item}
              </span>
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
