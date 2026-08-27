import { Reveal } from "./reveal";
import { security } from "@/lib/landing-content";
import { Shield, Check, ShieldCheck } from "lucide-react";

const frameworks = [
  { name: "SOC 2", status: "Type II certified" },
  { name: "EU AI Act", status: "Compliant" },
  { name: "ISO 42001", status: "In progress" },
  { name: "NIST AI RMF", status: "Aligned" },
  { name: "GDPR", status: "Compliant" },
];

export function SecuritySection() {
  const mid = Math.ceil(security.bullets.length / 2);
  const leftCol = security.bullets.slice(0, mid);
  const rightCol = security.bullets.slice(mid);

  return (
    <section id="security" className="border-t border-slate-200 py-24 md:py-32 bg-white">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-12 lg:grid-cols-2 lg:gap-16 items-start">
          <Reveal>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
                {security.eyebrow}
              </p>
              <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                {security.headline}
              </h2>

              <div className="mt-8 grid gap-x-8 gap-y-2 sm:grid-cols-2">
                {leftCol.map((bullet) => (
                  <div
                    key={bullet}
                    className="flex items-start gap-3 rounded-lg px-3 py-2 -mx-3 transition-colors duration-200 hover:bg-indigo-50/50"
                  >
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
                    <span className="text-sm leading-relaxed text-slate-600">{bullet}</span>
                  </div>
                ))}
                {rightCol.map((bullet) => (
                  <div
                    key={bullet}
                    className="flex items-start gap-3 rounded-lg px-3 py-2 -mx-3 transition-colors duration-200 hover:bg-indigo-50/50"
                  >
                    <Check className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
                    <span className="text-sm leading-relaxed text-slate-600">{bullet}</span>
                  </div>
                ))}
              </div>

              {/* Certification badges */}
              <div className="mt-8 flex flex-wrap gap-2">
                {security.badges.map((badge) => (
                  <span
                    key={badge}
                    className="inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-3.5 py-1.5 text-xs font-semibold text-indigo-700"
                  >
                    <ShieldCheck className="h-3.5 w-3.5" />
                    {badge}
                  </span>
                ))}
              </div>
            </div>
          </Reveal>

          <Reveal delay={100}>
            <div className="relative">
              <div className="absolute -inset-x-6 -inset-y-6 bg-gradient-to-bl from-indigo-50/80 via-transparent to-transparent rounded-3xl blur-3xl" />
              <div className="relative rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="flex items-center gap-3 mb-6">
                  <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600">
                    <Shield className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">Framework Compliance</p>
                    <p className="text-xs text-slate-500">5 major frameworks · 1 unified audit layer</p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {frameworks.map((fw) => (
                    <div
                      key={fw.name}
                      className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 px-4 py-3 transition-all duration-200 hover:border-indigo-200 hover:bg-indigo-50/50"
                    >
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-indigo-100 text-indigo-600">
                        <Check className="h-4 w-4" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-slate-900 leading-tight">{fw.name}</p>
                        <p className="text-[11px] text-slate-500 leading-tight mt-0.5">{fw.status}</p>
                      </div>
                    </div>
                  ))}
                </div>

                <p className="mt-4 text-center text-[11px] text-slate-400">
                  <Check className="h-3 w-3 inline -mt-0.5 mr-1 text-emerald-500" />
                  Annual third-party penetration testing
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
