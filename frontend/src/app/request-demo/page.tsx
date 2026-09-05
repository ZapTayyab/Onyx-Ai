"use client";

import { useState } from "react";
import { Header } from "@/components/landing/header";
import { Footer } from "@/components/landing/footer";
import { Shield, Calendar, Check, ArrowRight } from "lucide-react";

export default function RequestDemoPage() {
  const [submitted, setSubmitted] = useState(false);

  if (submitted) {
    return (
      <div className="min-h-screen bg-slate-50 text-slate-900">
        <Header />
        <main className="pt-28 pb-20">
          <div className="mx-auto max-w-lg px-6 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-50 text-emerald-600 mx-auto">
              <Check className="h-8 w-8" />
            </div>
            <h1 className="mt-6 text-3xl font-bold text-slate-900">Thanks for your interest!</h1>
            <p className="mt-4 text-slate-600 leading-relaxed">
              We&apos;ve received your request and will reach out within 24 hours to schedule your
              personalized demo.
            </p>
            <a
              href="/"
              className="mt-8 inline-flex h-11 items-center justify-center gap-2 rounded-md bg-slate-900 px-6 text-sm font-medium text-white hover:bg-slate-800 transition-all"
            >
              Back to home
              <ArrowRight className="h-4 w-4" />
            </a>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />
      <main>
        <section className="border-b border-slate-200 bg-white pt-28 pb-16">
          <div className="mx-auto max-w-7xl px-6">
            <div className="mx-auto max-w-2xl text-center">
              <div className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600 mb-6">
                <Shield className="h-3 w-3" />
                Request a demo
              </div>
              <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
                See Onyx in action.
              </h1>
              <p className="mt-4 text-lg text-slate-600">
                Book a 30-minute demo. We&apos;ll run a sample evaluation against your agent — no commitment required.
              </p>
            </div>
          </div>
        </section>

        <section className="py-16 md:py-20">
          <div className="mx-auto max-w-7xl px-6">
            <div className="grid gap-12 lg:grid-cols-2 lg:gap-16">
              <div>
                <div className="rounded-xl border border-slate-200 bg-white p-8">
                  <div className="grid gap-6 sm:grid-cols-2">
                    <div>
                      <label htmlFor="firstName" className="block text-sm font-medium text-slate-700">
                        First name
                      </label>
                      <input
                        id="firstName"
                        type="text"
                        className="mt-1 block w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                        placeholder="Jane"
                      />
                    </div>
                    <div>
                      <label htmlFor="lastName" className="block text-sm font-medium text-slate-700">
                        Last name
                      </label>
                      <input
                        id="lastName"
                        type="text"
                        className="mt-1 block w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                        placeholder="Doe"
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <label htmlFor="email" className="block text-sm font-medium text-slate-700">
                        Work email
                      </label>
                      <input
                        id="email"
                        type="email"
                        className="mt-1 block w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                        placeholder="jane@company.com"
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <label htmlFor="company" className="block text-sm font-medium text-slate-700">
                        Company name
                      </label>
                      <input
                        id="company"
                        type="text"
                        className="mt-1 block w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
                        placeholder="Acme Corp"
                      />
                    </div>
                    <div className="sm:col-span-2">
                      <label htmlFor="message" className="block text-sm font-medium text-slate-700">
                        What would you like to see?
                      </label>
                      <textarea
                        id="message"
                        rows={3}
                        className="mt-1 block w-full rounded-lg border border-slate-200 px-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100 resize-none"
                        placeholder="Tell us about your AI agent and what you're looking to evaluate..."
                      />
                    </div>
                  </div>
                  <button
                    onClick={() => setSubmitted(true)}
                    className="mt-6 inline-flex w-full h-11 items-center justify-center gap-2 rounded-md bg-blue-600 px-6 text-sm font-medium text-white transition-all hover:bg-blue-500 hover:shadow-[0_0_20px_-5px] hover:shadow-blue-500/40"
                  >
                    <Calendar className="h-4 w-4" />
                    Request demo
                  </button>
                </div>
              </div>

              <div className="flex flex-col justify-center">
                <h2 className="text-2xl font-bold tracking-tight text-slate-900">
                  What to expect from your demo:
                </h2>
                <ul className="mt-8 space-y-4">
                  {[
                    "A 30-minute walkthrough tailored to your use case",
                    "Live evaluation of your AI agent with synthetic personas",
                    "Review of regression detection and audit reporting",
                    "Q&A with our engineering team",
                    "No commitment — no sales pitch, just the product",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-3">
                      <Check className="mt-0.5 h-4 w-4 shrink-0 text-blue-600" />
                      <span className="text-sm text-slate-600">{item}</span>
                    </li>
                  ))}
                </ul>
                <div className="mt-8 rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <p className="text-xs text-slate-500 leading-relaxed">
                    <span className="font-semibold text-slate-700">Built for SOC 2 readiness.</span> Your data is encrypted in transit (TLS).
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
