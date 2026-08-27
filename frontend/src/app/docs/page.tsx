import { Header } from "@/components/landing/header";
import { Footer } from "@/components/landing/footer";
import { BookOpen, Search, ArrowRight } from "lucide-react";

const categories = [
  { title: "Getting Started", count: 6 },
  { title: "Core Concepts", count: 4 },
  { title: "Synthetic Personas", count: 3 },
  { title: "Chaos Injection", count: 2 },
  { title: "CI/CD Integration", count: 5 },
  { title: "API Reference", count: 12 },
  { title: "Compliance & Audit", count: 4 },
  { title: "Troubleshooting", count: 3 },
];

const articles = [
  { category: "Getting Started", title: "Quickstart: Your First Evaluation in 5 Minutes", readTime: "5 min" },
  { category: "Getting Started", title: "Platform Overview & Architecture", readTime: "8 min" },
  { category: "Getting Started", title: "Setting Up Your Project", readTime: "4 min" },
  { category: "Core Concepts", title: "Understanding Deterministic Evaluation", readTime: "6 min" },
  { category: "Core Concepts", title: "LLM-as-a-Judge Scoring Explained", readTime: "7 min" },
  { category: "Synthetic Personas", title: "Persona Types & Configuration", readTime: "10 min" },
  { category: "API Reference", title: "REST API: Endpoints & Authentication", readTime: "15 min" },
];

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />
      <main>
        <section className="border-b border-slate-200 bg-white pt-28 pb-16">
          <div className="mx-auto max-w-7xl px-6">
            <div className="mx-auto max-w-2xl text-center">
              <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600 mb-6">
                <BookOpen className="h-3 w-3" />
                Documentation
              </div>
              <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
                Everything you need to deploy with confidence.
              </h1>
              <p className="mt-4 text-lg leading-relaxed text-slate-600">
                Guides, API references, and best practices for integrating Onyx into your evaluation pipeline.
              </p>
              <div className="mt-8 relative mx-auto max-w-xl">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search documentation..."
                  className="w-full rounded-lg border border-slate-200 bg-white py-3 pl-11 pr-4 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                />
              </div>
            </div>
          </div>
        </section>

        <section className="py-16 md:py-20">
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {categories.map((cat) => (
                <a
                  key={cat.title}
                  href={`/docs/${cat.title.toLowerCase().replace(/\s+/g, "-")}`}
                  className="group rounded-xl border border-slate-200 bg-white p-5 transition-all hover:border-blue-200 hover:shadow-sm"
                >
                  <h3 className="text-sm font-semibold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {cat.title}
                  </h3>
                  <p className="mt-1 text-xs text-slate-500">{cat.count} articles</p>
                </a>
              ))}
            </div>
          </div>
        </section>

        <section className="border-t border-slate-200 py-16 md:py-20 bg-white">
          <div className="mx-auto max-w-7xl px-6">
            <h2 className="text-xl font-semibold text-slate-900">Popular articles</h2>
            <div className="mt-8 divide-y divide-slate-100">
              {articles.map((article) => (
                <a
                  key={article.title}
                  href={`/docs/${article.title.toLowerCase().replace(/\s+/g, "-")}`}
                  className="flex items-center justify-between py-4 group"
                >
                  <div>
                    <p className="text-xs font-medium text-blue-600 uppercase tracking-wider">{article.category}</p>
                    <p className="mt-0.5 text-sm font-medium text-slate-900 group-hover:text-blue-600 transition-colors">
                      {article.title}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-slate-400">{article.readTime}</span>
                    <ArrowRight className="h-4 w-4 text-slate-300 group-hover:text-blue-500 transition-colors" />
                  </div>
                </a>
              ))}
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
