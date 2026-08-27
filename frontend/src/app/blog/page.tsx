import { Header } from "@/components/landing/header";
import { Footer } from "@/components/landing/footer";
import { Calendar, Clock, ArrowRight, Shield } from "lucide-react";

const posts = [
  {
    title: "Why Deterministic Evaluation Matters for Production AI Agents",
    excerpt: "How non-deterministic LLM outputs create risk in production, and why a repeatable evaluation pipeline is the only way to catch regressions before they ship.",
    date: "Jun 22, 2026",
    readTime: "8 min read",
    category: "Engineering",
    author: "Sarah Chen",
  },
  {
    title: "Introducing Chaos Injection for LLM Agents",
    excerpt: "Our new chaos engineering module lets you test how your agent behaves under real-world stress conditions — latency spikes, context bloat, and guardrail interruptions.",
    date: "Jun 15, 2026",
    readTime: "6 min read",
    category: "Product",
    author: "Marcus Rivera",
  },
  {
    title: "SOC 2 Compliance for AI Agents: A Practical Guide",
    excerpt: "What AI assurance teams need to know about SOC 2 compliance, from audit logging requirements to evidence collection for AI-driven systems.",
    date: "Jun 8, 2026",
    readTime: "10 min read",
    category: "Compliance",
    author: "Aisha Patel",
  },
  {
    title: "LLM-as-a-Judge: Building a Reliable Scoring Engine",
    excerpt: "A deep dive into dual-mode scoring — combining rule-based evaluation with LLM fallback for consistent, auditable grading of agent responses.",
    date: "May 28, 2026",
    readTime: "12 min read",
    category: "Engineering",
    author: "Sarah Chen",
  },
  {
    title: "Reducing Production Incidents by 60% with Automated Testing",
    excerpt: "How one financial services team cut AI agent incidents by 60% in three months using deterministic evaluation and CI/CD gating.",
    date: "May 18, 2026",
    readTime: "7 min read",
    category: "Case Study",
    author: "David Kim",
  },
  {
    title: "Synthetic Personas: Testing Beyond Happy Path",
    excerpt: "Why standard test cases miss the edge cases that cause production failures, and how synthetic personas help you find them before they reach users.",
    date: "May 10, 2026",
    readTime: "9 min read",
    category: "Best Practices",
    author: "Marcus Rivera",
  },
];

const categories = ["All", "Engineering", "Product", "Compliance", "Case Study", "Best Practices"];

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />
      <main>
        <section className="border-b border-slate-200 bg-white pt-28 pb-16">
          <div className="mx-auto max-w-7xl px-6 text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600 mb-6">
              <Shield className="h-3 w-3" />
              Blog
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Insights from the team behind Onyx.
            </h1>
            <p className="mt-4 text-lg text-slate-600 max-w-xl mx-auto">
              Engineering deep-dives, compliance guides, and best practices for AI assurance.
            </p>
          </div>
        </section>

        <section className="py-16 md:py-20">
          <div className="mx-auto max-w-7xl px-6">
            <div className="flex flex-wrap gap-2 mb-12">
              {categories.map((cat) => (
                <button
                  key={cat}
                  className={`rounded-full px-4 py-1.5 text-xs font-medium transition-colors ${
                    cat === "All"
                      ? "bg-blue-600 text-white"
                      : "bg-white border border-slate-200 text-slate-600 hover:border-slate-300"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
              {posts.map((post) => (
                <a
                  key={post.title}
                  href={`/blog/${post.title.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "")}`}
                  className="group rounded-xl border border-slate-200 bg-white p-6 transition-all hover:border-blue-200 hover:shadow-sm"
                >
                  <div className="flex items-center gap-2 text-xs text-slate-500 mb-3">
                    <span className="font-medium text-blue-600">{post.category}</span>
                    <span>&middot;</span>
                    <Calendar className="h-3 w-3" />
                    <span>{post.date}</span>
                  </div>
                  <h2 className="text-base font-semibold text-slate-900 group-hover:text-blue-600 transition-colors leading-snug">
                    {post.title}
                  </h2>
                  <p className="mt-2 text-sm leading-relaxed text-slate-600 line-clamp-2">
                    {post.excerpt}
                  </p>
                  <div className="mt-4 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-xs text-slate-400">
                      <Clock className="h-3 w-3" />
                      <span>{post.readTime}</span>
                      <span>&middot;</span>
                      <span>{post.author}</span>
                    </div>
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
