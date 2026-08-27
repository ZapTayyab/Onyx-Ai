import { Header } from "@/components/landing/header";
import { Hero } from "@/components/landing/hero";
import { LogoStrip } from "@/components/landing/logo-strip";
import { ProblemSection } from "@/components/landing/problem-section";
import { HowItWorks } from "@/components/landing/how-it-works";
import { Capabilities } from "@/components/landing/capabilities";
import { SecuritySection } from "@/components/landing/security-section";
import { DocsSection } from "@/components/landing/docs-section";
import { PricingSection } from "@/components/landing/pricing-section";
import { BlogSection } from "@/components/landing/blog-section";
import { CTASection } from "@/components/landing/cta-section";
import { Footer } from "@/components/landing/footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />
      <main>
        <Hero />
        <LogoStrip />
        <ProblemSection />
        <HowItWorks />
        <Capabilities />
        <SecuritySection />
        <DocsSection />
        <PricingSection />
        <BlogSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
}
