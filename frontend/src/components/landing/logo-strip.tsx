import { trustBar } from "@/lib/landing-content";

const duplicatedLogos = [...trustBar.logos, ...trustBar.logos, ...trustBar.logos];

export function LogoStrip() {
  return (
    <section className="border-t border-b border-slate-200 bg-white py-14 overflow-hidden">
      <div className="mx-auto max-w-7xl px-6">
        <p className="text-center text-xs font-medium uppercase tracking-widest text-indigo-500 mb-10 max-w-2xl mx-auto leading-relaxed">
          {trustBar.heading}
        </p>

        <div className="relative">
          <div className="flex marquee gap-20">
            {duplicatedLogos.map((name, i) => (
              <div
                key={`${name}-${i}`}
                className="shrink-0 text-sm font-bold tracking-[0.15em] text-indigo-800/75 uppercase select-none whitespace-nowrap"
                style={{
                  filter: "brightness(0) saturate(100%) invert(30%) sepia(50%) saturate(1500%) hue-rotate(225deg) brightness(90%) contrast(90%)",
                  opacity: 0.75,
                }}
              >
                {name}
              </div>
            ))}
          </div>
        </div>
      </div>

      <style>{`
        .marquee {
          animation: marquee-scroll 28s linear infinite;
          width: max-content;
        }
        @keyframes marquee-scroll {
          0% { transform: translateX(0); }
          100% { transform: translateX(-33.33%); }
        }
      `}</style>
    </section>
  );
}
