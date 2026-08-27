import { Reveal } from "./reveal";
import { problemStatement } from "@/lib/landing-content";
import { TriangleAlert, EyeOff, OctagonX, ArrowRight, AlertCircle } from "lucide-react";

const iconMap: Record<string, React.ReactNode> = {
  TriangleAlert: <TriangleAlert className="h-7 w-7" />,
  EyeOff: <EyeOff className="h-7 w-7" />,
  OctagonX: <OctagonX className="h-7 w-7" />,
};

export function ProblemSection() {
  return (
    <section id="product" className="relative overflow-hidden bg-slate-950 py-24 md:py-32">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,rgba(220,38,38,0.15),transparent_70%)]" />
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(234,179,8,0.08),transparent_50%)]" />
      <div className="pointer-events-none absolute -top-40 -right-40 h-80 w-80 rounded-full bg-red-500/10 blur-3xl animate-pulse" />
      <div className="pointer-events-none absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-amber-500/10 blur-3xl" />

      <div className="relative mx-auto max-w-7xl px-6">
        <Reveal>
          <div className="mx-auto max-w-3xl text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-red-800/50 bg-red-950/50 px-4 py-1.5 text-xs font-medium text-red-300 mb-6 backdrop-blur-sm">
              <AlertCircle className="h-3.5 w-3.5" />
              {problemStatement.eyebrow}
            </div>
            <h2 className="text-4xl font-bold tracking-tight text-white sm:text-5xl leading-tight">
              {problemStatement.headline}
            </h2>
          </div>
        </Reveal>

        <div className="mt-20 grid gap-8 md:grid-cols-3">
          {problemStatement.cards.map((card, i) => (
            <Reveal key={card.title} delay={i * 120}>
              <div
                className="group relative overflow-hidden rounded-2xl p-8 transition-all duration-500 hover:-translate-y-1 hover:shadow-[0_0_40px_-10px] hover:shadow-red-500/20"
                style={{
                  border: "1px solid rgba(255, 255, 255, 0.08)",
                  backdropFilter: "blur(12px)",
                  WebkitBackdropFilter: "blur(12px)",
                  background: "rgba(255, 255, 255, 0.04)",
                }}
              >
                <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-red-500/5 to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100" />
                <div className="pointer-events-none absolute -inset-1 bg-red-500/5 blur-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100" />

                <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-red-500/15 text-red-400 ring-1 ring-red-500/20 transition-all duration-500 group-hover:bg-red-500/25 group-hover:ring-red-400/30 group-hover:text-red-300 group-hover:scale-110">
                  {iconMap[card.icon]}
                </div>

                <h3 className="mt-6 text-lg font-bold text-white">
                  {card.title}
                </h3>

                <p className="mt-3 text-sm leading-relaxed text-slate-400 transition-colors duration-500 group-hover:text-slate-300">
                  {card.description}
                </p>

                <div className="mt-6 flex items-center gap-1.5 text-xs font-medium text-red-400 opacity-0 transition-all duration-500 group-hover:opacity-100 -translate-x-1 group-hover:translate-x-0">
                  <span>The cost of silence</span>
                  <ArrowRight className="h-3 w-3" />
                </div>
              </div>
            </Reveal>
          ))}
        </div>

        <Reveal delay={400}>
          <div className="relative mt-20 mx-auto max-w-2xl">
            <div
              className="relative rounded-xl p-6 text-center backdrop-blur-sm"
              style={{
                border: "1px solid rgba(220, 38, 38, 0.3)",
                background: "rgba(220, 38, 38, 0.1)",
                backdropFilter: "blur(12px)",
                WebkitBackdropFilter: "blur(12px)",
              }}
            >
              <p className="text-sm text-slate-400 leading-relaxed">
                The average AI incident costs{' '}
                <span className="font-semibold text-red-300">$2.3 million</span>{' '}
                in remediation, compliance fines, and reputational damage.{' '}
                <span className="text-slate-300">Most teams find out the hard way.</span>
              </p>
              <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 h-0 w-0 border-l-8 border-r-8 border-t-8 border-transparent border-t-red-950/30" />
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}
