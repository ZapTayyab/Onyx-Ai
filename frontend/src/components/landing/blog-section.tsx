import { blogOverview } from "@/lib/landing-content";
import { Calendar, Clock, ArrowRight } from "lucide-react";

const categoryColors: Record<string, string> = {
  Research: "bg-indigo-500 text-white",
  Tutorial: "bg-cyan-500 text-white",
  Compliance: "bg-amber-500 text-white",
};

export function BlogSection() {
  const featured = blogOverview.posts.find((p) => (p as any).featured);
  const others = blogOverview.posts.filter((p) => !(p as any).featured);

  return (
    <section id="blog" className="border-t border-slate-200 py-24 md:py-32 bg-white">
      <div className="mx-auto max-w-7xl px-6">
        <div className="mx-auto max-w-2xl text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-indigo-600">
            {blogOverview.eyebrow}
          </p>
          <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            {blogOverview.headline}
          </h2>
        </div>

        <div className="mt-16 grid gap-6 lg:grid-cols-2">
          {/* Featured card */}
          {featured && (
            <a
              href={`/blog/${featured.title.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "")}`}
              className="group relative lg:row-span-2 rounded-2xl border border-slate-200 bg-slate-50 p-8 transition-all duration-500 hover:border-indigo-300 hover:shadow-lg hover:-translate-y-0.5 flex flex-col"
            >
              <div className="flex items-center gap-3 mb-4">
                <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${categoryColors[featured.category] || "bg-indigo-100 text-indigo-700"}`}>
                  {featured.category}
                </span>
                <span className="text-xs text-slate-400">{featured.date}</span>
              </div>

              <h3 className="text-2xl font-bold text-slate-900 leading-tight group-hover:text-indigo-600 transition-colors">
                {featured.title}
              </h3>

              <p className="mt-3 text-sm leading-relaxed text-slate-600 flex-1">
                {(featured as any).excerpt}
              </p>

              <div className="mt-6 flex items-center gap-4 text-xs text-slate-400">
                <span className="flex items-center gap-1.5 font-mono tracking-tight text-slate-400">
                  <Clock className="h-3 w-3" />
                  {(featured as any).readTime}
                </span>
                <span className="flex items-center gap-1.5">
                  <span className="h-5 w-5 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-[10px] font-bold">
                    {(featured as any).author?.charAt(0) || "S"}
                  </span>
                  {(featured as any).author || "Sarah Chen"}
                </span>
                <ArrowRight className="h-4 w-4 ml-auto text-indigo-400 group-hover:translate-x-1 transition-transform" />
              </div>
            </a>
          )}

          {/* Side grid */}
          <div className="flex flex-col gap-6">
            {others.map((post) => (
              <a
                key={post.title}
                href={`/blog/${post.title.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "")}`}
                className="group rounded-xl border border-slate-200 bg-white p-6 transition-all duration-300 hover:border-indigo-200 hover:shadow-sm hover:-translate-y-0.5 flex-1 flex flex-col"
              >
                <div className="flex items-center gap-2 mb-3">
                  <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-semibold ${categoryColors[post.category] || "bg-indigo-100 text-indigo-700"}`}>
                    {post.category}
                  </span>
                  <span className="text-xs text-slate-400">{post.date}</span>
                </div>
                <h3 className="text-base font-bold text-slate-900 group-hover:text-indigo-600 transition-colors leading-snug flex-1">
                  {post.title}
                </h3>
                <div className="mt-3 flex items-center gap-3 text-xs text-slate-400">
                  <span className="flex items-center gap-1 font-mono tracking-tight text-slate-400">
                    <Clock className="h-3 w-3" />
                    {post.readTime || "6 min read"}
                  </span>
                  <ArrowRight className="h-3.5 w-3.5 ml-auto text-indigo-300 group-hover:translate-x-1 transition-transform" />
                </div>
              </a>
            ))}
          </div>
        </div>

        <div className="mt-10 text-center">
          <a
            href="/blog"
            className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-300 bg-white px-5 text-sm font-medium text-slate-800 transition-all hover:bg-slate-50 hover:shadow-sm"
          >
            Read all posts
            <ArrowRight className="h-4 w-4" />
          </a>
        </div>
      </div>
    </section>
  );
}
