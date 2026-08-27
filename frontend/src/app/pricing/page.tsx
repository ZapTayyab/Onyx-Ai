import { Header } from "@/components/landing/header";
import { Footer } from "@/components/landing/footer";
import { Check, ArrowRight, Shield } from "lucide-react";

const plans = [
  {
    name: "Starter",
    price: "$499",
    period: "/month",
    description: "For teams getting started with AI assurance.",
    features: [
      "Up to 1,000 evaluations / month",
      "5 synthetic personas",
      "LLM-as-a-Judge scoring",
      "Basic regression detection",
      "Email support",
    ],
    cta: "Start free trial",
    popular: false,
  },
  {
    name: "Professional",
    price: "$1,499",
    period: "/month",
    description: "For growing teams that need robust assurance.",
    features: [
      "Up to 10,000 evaluations / month",
      "15 synthetic personas",
      "Chaos injection testing",
      "CI/CD integration (GitHub, GitLab)",
      "Slack & email support",
      "Audit-ready reports",
    ],
    cta: "Start free trial",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    description: "For organizations with advanced security and compliance needs.",
    features: [
      "Unlimited evaluations",
      "Custom persona development",
      "SSO / SAML / OIDC",
      "Dedicated infrastructure",
      "24/7 premium support",
      "Custom integrations",
      "On-premise deployment option",
      "Dedicated success manager",
    ],
    cta: "Contact sales",
    popular: false,
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />
      <main>
        <section className="border-b border-slate-200 bg-white pt-28 pb-16">
          <div className="mx-auto max-w-7xl px-6 text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600 mb-6">
              <Shield className="h-3 w-3" />
              Pricing
            </div>
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Simple, transparent pricing.
            </h1>
            <p className="mt-4 text-lg text-slate-600 max-w-xl mx-auto">
              Start with a free trial. No credit card required. Scale as your assurance needs grow.
            </p>
          </div>
        </section>

        <section className="py-16 md:py-24">
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid gap-8 lg:grid-cols-3">
              {plans.map((plan) => (
                <div
                  key={plan.name}
                  className={`relative rounded-2xl border p-8 transition-all ${
                    plan.popular
                      ? "border-blue-200 bg-white shadow-lg shadow-blue-100/50 scale-105"
                      : "border-slate-200 bg-white"
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-blue-600 px-4 py-1 text-xs font-medium text-white">
                      Most popular
                    </div>
                  )}
                  <h2 className="text-lg font-semibold text-slate-900">{plan.name}</h2>
                  <div className="mt-4 flex items-baseline gap-1">
                    <span className="text-4xl font-bold text-slate-900">{plan.price}</span>
                    {plan.period && (
                      <span className="text-sm text-slate-500">{plan.period}</span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-slate-600">{plan.description}</p>
                  <ul className="mt-8 space-y-3">
                    {plan.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-3">
                        <Check className="mt-0.5 h-4 w-4 shrink-0 text-blue-600" />
                        <span className="text-sm text-slate-600">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  <a
                    href="/request-demo"
                    className={`mt-8 inline-flex w-full h-11 items-center justify-center gap-2 rounded-md text-sm font-medium transition-all ${
                      plan.popular
                        ? "bg-blue-600 text-white hover:bg-blue-500 hover:shadow-[0_0_20px_-5px] hover:shadow-blue-500/40"
                        : "border border-slate-300 bg-white text-slate-800 hover:bg-slate-50"
                    }`}
                  >
                    {plan.cta}
                    <ArrowRight className="h-4 w-4" />
                  </a>
                </div>
              ))}
            </div>

            <div className="mt-16 rounded-xl border border-slate-200 bg-white p-8 text-center">
              <h3 className="text-lg font-semibold text-slate-900">Need a custom plan?</h3>
              <p className="mt-2 text-sm text-slate-600">
                We offer custom pricing for large-scale deployments, research institutions, and non-profits.
              </p>
              <a
                href="/request-demo"
                className="mt-4 inline-flex h-10 items-center justify-center rounded-md bg-slate-900 px-6 text-sm font-medium text-white hover:bg-slate-800 transition-all"
              >
                Contact us
              </a>
            </div>
          </div>
        </section>

        <section className="border-t border-slate-200 py-16 bg-slate-100">
          <div className="mx-auto max-w-7xl px-6 text-center">
            <h2 className="text-lg font-semibold text-slate-900">Trusted by enterprise teams</h2>
            <p className="mt-2 text-sm text-slate-600">
              SOC 2 compliant · SSO / SAML / OIDC · Immutable audit logging · Data residency controls
            </p>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
