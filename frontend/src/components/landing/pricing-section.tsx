"use client";

import { useState } from "react";
import { pricingOverview } from "@/lib/landing-content";
import { Check, Minus, ArrowRight, Shield } from "lucide-react";

export function PricingSection() {
  const [annual, setAnnual] = useState(true);

  return (
    <section id="pricing" className="border-t border-slate-200 py-24 md:py-32 bg-slate-50">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
            {pricingOverview.eyebrow}
          </p>
          <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            {pricingOverview.headline}
          </h2>
        </div>

        {/* Annual / Monthly toggle */}
        <div className="mt-10 flex items-center justify-center gap-4">
          <span className={`text-sm font-medium transition-colors ${annual ? "text-slate-900" : "text-slate-400"}`}>
            Annual
          </span>
          <button
            onClick={() => setAnnual(!annual)}
            className="relative h-7 w-12 rounded-full bg-indigo-600 transition-colors"
          >
            <span
              className={`absolute top-0.5 h-6 w-6 rounded-full bg-white shadow-sm transition-transform duration-200 ${
                annual ? "left-0.5" : "left-[1.35rem]"
              }`}
            />
          </button>
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium transition-colors ${!annual ? "text-slate-900" : "text-slate-400"}`}>
              Monthly
            </span>
            <span className="inline-flex items-center rounded-full bg-emerald-100 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider text-emerald-700">
              Save 20%
            </span>
          </div>
        </div>

        {/* Pricing cards */}
        <div className="mt-12 grid gap-6 lg:grid-cols-3 items-stretch">
          {pricingOverview.plans.map((plan) => {
            const price = annual ? plan.annual : plan.monthly;
            const isPopular = (plan as any).popular;

            return (
              <div
                key={plan.name}
                className={`relative rounded-2xl transition-all duration-300 flex flex-col ${
                  isPopular
                    ? "border-2 border-indigo-500 bg-indigo-50/40 shadow-lg shadow-indigo-100/60 scale-[1.02] lg:scale-105 z-10 p-8"
                    : "border border-slate-200 bg-white p-7 hover:border-slate-300"
                }`}
              >
                {isPopular && (
                  <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 rounded-full bg-indigo-600 px-4 py-1 text-xs font-semibold text-white shadow-sm whitespace-nowrap">
                    Most popular
                  </div>
                )}

                <h3 className={`font-bold ${isPopular ? "text-lg" : "text-base"} text-slate-900`}>
                  {plan.name}
                </h3>

                <div className="mt-4 flex items-baseline gap-1.5">
                  <span className={`font-bold text-slate-900 ${isPopular ? "text-4xl" : "text-3xl"}`}>
                    {price}
                  </span>
                  {plan.period && (
                    <span className="text-sm text-slate-500">{plan.period}</span>
                  )}
                </div>

                {isPopular && annual && (
                  <p className="mt-1 text-xs text-emerald-600 font-medium">
                    $1,499/mo monthly &middot; Save $300/mo
                  </p>
                )}

                <p className={`mt-1 ${isPopular ? "text-sm" : "text-sm"} text-slate-500`}>
                  {plan.description}
                </p>

                <ul className={`mt-8 space-y-3 flex-1`}>
                  {plan.features.map((feature) => (
                    <li key={feature.text} className="flex items-start gap-3">
                      {feature.included ? (
                        <Check className={`mt-0.5 h-4 w-4 shrink-0 text-indigo-600`} />
                      ) : (
                        <Minus className={`mt-0.5 h-4 w-4 shrink-0 text-slate-300`} />
                      )}
                      <span
                        className={`text-sm leading-snug ${
                          feature.included ? "text-slate-700" : "text-slate-400"
                        }`}
                      >
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>

                <a
                  href="/request-demo"
                  className={`mt-8 inline-flex w-full h-11 items-center justify-center gap-2 rounded-lg text-sm font-semibold transition-all ${
                    isPopular
                      ? "bg-indigo-600 text-white hover:bg-indigo-500 hover:shadow-[0_0_25px_-8px] hover:shadow-indigo-500/50"
                      : "border border-slate-300 bg-white text-slate-800 hover:bg-slate-50 hover:border-slate-400"
                  }`}
                >
                  {plan.name === "Enterprise" ? "Contact sales" : "Start free trial"}
                  <ArrowRight className="h-4 w-4" />
                </a>
              </div>
            );
          })}
        </div>

        {/* Trust line */}
        <div className="mt-12 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 rounded-xl border-2 border-indigo-100 bg-indigo-50/60 px-6 py-5 text-center shadow-sm">
          <Shield className="h-5 w-5 shrink-0 text-indigo-500" />
          <span className="text-sm font-medium text-indigo-800">
            {pricingOverview.trustLine}
          </span>
        </div>
      </div>
    </section>
  );
}
