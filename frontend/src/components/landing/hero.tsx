import { hero } from "@/lib/landing-content";
import { Shield, ArrowRight } from "lucide-react";

export function Hero() {
  return (
    <section className="relative min-h-screen overflow-hidden">
      <video
        autoPlay
        muted
        loop
        playsInline
        className="absolute inset-0 h-full w-full object-cover"
      >
        <source src="/hero/hero-loop.mp4" type="video/mp4" />
      </video>

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col justify-center px-6 pt-24 pb-20 md:pt-28 md:pb-28">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/90 backdrop-blur-sm px-3 py-1 text-xs font-medium text-gray-700 mb-6 shadow-sm">
            <Shield className="h-3 w-3 text-blue-600" />
            Enterprise AI Assurance Platform
          </div>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl leading-tight">
            <span className="text-gray-900">Deterministic </span>
            <span className="text-blue-600">Assurance for AI </span>
            <span className="text-gray-900">Agents in Production</span>
          </h1>
          <p className="mt-6 text-lg leading-relaxed text-gray-700 max-w-xl">
            {hero.subheadline}
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <a
              href={hero.cta.href}
              className="inline-flex h-11 items-center justify-center gap-2 rounded-md bg-gray-900 px-6 text-sm font-medium text-white transition-all hover:bg-gray-800 hover:shadow-[0_0_25px_-5px] hover:shadow-gray-900/30"
            >
              {hero.cta.label}
              <ArrowRight className="h-4 w-4" />
            </a>
            <a
              href={hero.ctaSecondary.href}
              className="inline-flex h-11 items-center justify-center rounded-md border border-gray-300 bg-white/80 backdrop-blur-sm px-6 text-sm font-medium text-gray-800 transition-all hover:bg-white hover:shadow-sm"
            >
              {hero.ctaSecondary.label}
            </a>
          </div>
          <div className="mt-8 flex flex-wrap gap-2">
            {hero.trustPills.map((pill) => (
              <a
                key={pill}
                href="#security"
                className="inline-flex items-center rounded-full border border-gray-200 bg-white/80 backdrop-blur-sm px-3 py-1 text-xs text-gray-600 shadow-sm transition-colors hover:bg-white hover:text-gray-900"
              >
                {pill}
              </a>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
