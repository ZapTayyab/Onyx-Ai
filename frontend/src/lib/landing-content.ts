export const siteConfig = {
  name: "Onyx",
  tagline: "Enterprise AI Assurance Platform",
  url: "https://snt.ai",
};

export const navLinks = [
  { href: "#product", label: "Product" },
  { href: "#docs", label: "Docs" },
  { href: "#pricing", label: "Pricing" },
  { href: "#blog", label: "Blog" },
  { href: "/login", label: "Sign in", variant: "ghost" as const },
  { href: "/request-demo", label: "Request demo", variant: "primary" as const },
];

export const hero = {
  headline: "Deterministic Assurance for AI Agents in Production",
  subheadline:
    "Onyx replaces manual red-teaming with a repeatable, auditable evaluation pipeline. Stress-test your LLMs using synthetic personas, chaos injection, and LLM-as-a-Judge grading \u2014 all gated in CI/CD.",
  cta: { label: "Request a demo", href: "/request-demo" },
  ctaSecondary: { label: "View documentation", href: "/docs" },
  trustPills: [
    "SOC 2 compliant",
    "SSO / SAML / OIDC",
    "Role-based access control",
    "Immutable audit logging",
  ],
};

export const trustBar = {
  heading: "Engineering and AI governance teams at leading enterprises run on Onyx",
  logos: [
    "Enterprise Corp",
    "SecureFin",
    "HealthBridge AI",
    "DefenseLogix",
    "ComplianceFirst",
  ],
};

export const problemStatement = {
  eyebrow: "The problem",
  headline: "Your AI agent is flying blind — and it's only a matter of time.",
  cards: [
    {
      title: "Unpredictable outputs",
      description:
        "Same prompt, different answer. Every model update, temperature tweak, or latency spike silently shifts behavior. You won't know it broke until a customer screams — and by then, the damage is done.",
      icon: "TriangleAlert" as const,
    },
    {
      title: "Zero audit trail",
      description:
        "When things go wrong — and they will — you can't trace a thing. No attribution. No reproduction. No compliance evidence. Just a black box and a room full of people pointing fingers at each other.",
      icon: "EyeOff" as const,
    },
    {
      title: "No safety net",
      description:
        "Deployments ship without any automated validation. No gate. No regression check. No safety net. Every push is a roll of the dice — and the house always wins eventually.",
      icon: "OctagonX" as const,
    },
  ],
};

export type Phase = "generation" | "execution" | "output";

export interface PipelineStep {
  number: string;
  title: string;
  description: string;
  icon: string;
  phase: Phase;
  duration?: string;
}

export const pipelineSteps: PipelineStep[] = [
  {
    number: "01",
    title: "Persona Generation",
    description: "Synthesize 8+ user archetypes across standard, edge-case, and adversarial categories.",
    icon: "Users",
    phase: "generation",
  },
  {
    number: "02",
    title: "Scenario Execution",
    description: "Run multi-turn conversations against your agent, simulating realistic interaction flows.",
    icon: "Play",
    phase: "generation",
  },
  {
    number: "03",
    title: "Chaos Injection",
    description: "Introduce latency, context bloat, and guardrail interruptions to test resilience under stress.",
    icon: "Activity",
    phase: "execution",
    duration: "~0.3s",
  },
  {
    number: "04",
    title: "LLM-as-a-Judge",
    description: "Dual-mode scoring \u2014 rule-based and LLM fallback \u2014 evaluates groundedness, compliance, and robustness.",
    icon: "Scale",
    phase: "execution",
    duration: "~1.2s",
  },
  {
    number: "05",
    title: "Regression Detection",
    description: "Z-score anomaly detection across runs with persona-level thresholds and automated alerting.",
    icon: "TrendingDown",
    phase: "output",
  },
  {
    number: "06",
    title: "Audit Export",
    description: "Generate JUnit XML reports, signed evidence snapshots, and one-click compliance packages.",
    icon: "FileText",
    phase: "output",
    duration: "~2min",
  },
];

export const pipelinePhases = [
  { key: "generation" as Phase, label: "Generation", stages: "01\u201302" },
  { key: "execution" as Phase, label: "Execution", stages: "03\u201304" },
  { key: "output" as Phase, label: "Output", stages: "05\u201306" },
];

export interface Capability {
  title: string;
  description: string;
  outcome: string;
  icon: string;
  metric: { value: string; label: string };
  featured?: boolean;
}

export const capabilities: Capability[] = [
  {
    title: "Synthetic Personas",
    description: "Simulate 8+ user archetypes \u2014 HelpSeeker, Jailbreaker, RapidTyper, and more \u2014 across standard, edge, and adversarial categories.",
    outcome: "Catch failure modes manual testing misses",
    icon: "UserCheck",
    metric: { value: "10,000+", label: "personas per audit" },
    featured: true,
  },
  {
    title: "Chaos Injection",
    description: "Programmatically inject latency, context bloat, and guardrail interruptions to test your agent\u2019s resilience under real-world stress.",
    outcome: "Reduce production incidents by up to 60%",
    icon: "Zap",
    metric: { value: "99.4%", label: "injection coverage" },
    featured: true,
  },
  {
    title: "LLM-as-a-Judge",
    description: "Dual-mode scoring engine evaluates groundedness, instruction compliance, and adversarial robustness \u2014 rule-based with LLM fallback.",
    outcome: "Consistent, auditable scoring across every run",
    icon: "Scale",
    metric: { value: "99.7%", label: "scoring accuracy" },
  },
  {
    title: "Regression Detection",
    description: "Statistical anomaly detection with persona-level thresholds. Automatically flag score drops, latency regressions, and behavioral drift.",
    outcome: "Ship with confidence, not guesswork",
    icon: "TrendingDown",
    metric: { value: "60%", label: "fewer incidents" },
  },
  {
    title: "CI/CD Gating",
    description: "JUnit XML output blocks deployments on score regression. Native integration with GitHub Actions, GitLab CI, and Jenkins.",
    outcome: "Gate releases on objective safety criteria",
    icon: "GitBranch",
    metric: { value: "< 2s", label: "per evaluation" },
  },
  {
    title: "Audit-Ready Evidence",
    description: "Immutable trace logs, hash-chain verified audit snapshots, and one-click compliance export for SOC 2, ISO 27001, and internal reviews.",
    outcome: "Hours of compliance prep reduced to minutes",
    icon: "FileText",
    metric: { value: "30s", label: "export vs 15min manual" },
  },
];

export const security = {
  eyebrow: "Security & Compliance",
  headline: "Governance built into every layer of the platform.",
  bullets: [
    "SOC 2 compliant \u2014 audit in progress with third-party examiner",
    "AES-256 encryption at rest and TLS 1.3 in transit",
    "SSO via SAML 2.0 and OIDC (Clerk, Auth0, Okta)",
    "Role-based access control \u2014 Owner, Admin, Member, Viewer",
    "Immutable audit logging with hash-chain verification",
    "Customer-managed encryption keys (AWS KMS, Azure Key Vault)",
    "Data residency controls \u2014 EU, US, and APAC regions",
    "Annual third-party penetration testing",
  ],
  badges: [
    "SOC 2 Type II",
    "ISO 42001",
    "End-to-end encrypted",
    "Zero data retention",
  ],
  frameworks: [
    { name: "SOC 2", x: 50, y: 5 },
    { name: "EU AI Act", x: 88, y: 22 },
    { name: "ISO 42001", x: 82, y: 72 },
    { name: "NIST AI RMF", x: 50, y: 92 },
    { name: "GDPR", x: 15, y: 72 },
  ],
};

export const docsOverview = {
  eyebrow: "Documentation",
  headline: "Everything you need to integrate and deploy.",
  categories: [
    { title: "Getting Started", count: 6, icon: "BookOpen" },
    { title: "API Reference", count: 12, icon: "Code" },
    { title: "CI/CD Integration", count: 5, icon: "GitBranch" },
    { title: "Compliance & Audit", count: 4, icon: "Shield" },
  ],
};

export const pricingOverview = {
  eyebrow: "Pricing",
  headline: "Simple, transparent pricing for every stage.",
  monthly: true,
  plans: [
    {
      name: "Starter",
      monthly: "$499",
      annual: "$399",
      period: "/month",
      description: "For teams getting started.",
      features: [
        { text: "Up to 1,000 evaluations / month", included: true },
        { text: "5 synthetic personas", included: true },
        { text: "LLM-as-a-Judge scoring", included: true },
        { text: "Email support", included: true },
        { text: "Chaos injection testing", included: false },
        { text: "CI/CD integration", included: false },
        { text: "Audit-ready reports", included: false },
        { text: "SSO / SAML / OIDC", included: false },
      ],
    },
    {
      name: "Professional",
      monthly: "$1,499",
      annual: "$1,199",
      period: "/month",
      description: "For growing teams.",
      features: [
        { text: "Up to 10,000 evaluations / month", included: true },
        { text: "15 synthetic personas", included: true },
        { text: "LLM-as-a-Judge scoring", included: true },
        { text: "Email & Slack support", included: true },
        { text: "Chaos injection testing", included: true },
        { text: "CI/CD integration", included: true },
        { text: "Audit-ready reports", included: true },
        { text: "SSO / SAML / OIDC", included: false },
      ],
      popular: true,
    },
    {
      name: "Enterprise",
      monthly: "Custom",
      annual: "Custom",
      period: "",
      description: "For advanced security needs.",
      features: [
        { text: "Unlimited evaluations", included: true },
        { text: "Custom persona development", included: true },
        { text: "LLM-as-a-Judge scoring", included: true },
        { text: "24/7 premium support", included: true },
        { text: "Chaos injection testing", included: true },
        { text: "CI/CD integration", included: true },
        { text: "Audit-ready reports", included: true },
        { text: "SSO / SAML / OIDC", included: true },
      ],
    },
  ],
  trustLine: "All plans include SOC 2 audit logging, encrypted model interactions, and a dedicated security review.",
};

export const blogOverview = {
  eyebrow: "Technical depth",
  headline: "From our research team.",
  posts: [
    {
      title: "Why Deterministic Evaluation Matters for Production AI Agents",
      date: "Jun 22, 2026",
      category: "Research",
      readTime: "8 min read",
      excerpt: "How non-deterministic LLM outputs create risk in production, and why a repeatable evaluation pipeline is the only way to catch regressions before they ship.",
      author: "Sarah Chen",
      featured: true,
    },
    {
      title: "Introducing Chaos Injection for LLM Agents",
      date: "Jun 15, 2026",
      category: "Tutorial",
      readTime: "6 min read",
    },
    {
      title: "SOC 2 Compliance for AI Agents: A Practical Guide",
      date: "Jun 8, 2026",
      category: "Compliance",
      readTime: "10 min read",
    },
  ],
};

export const cta = {
  headline: "Your next AI audit should produce proof, not hope.",
  subheadline:
    "Schedule a 30-minute technical walkthrough. Audit results in 24 hours.",
  primary: { label: "Request a demo", href: "/request-demo" },
  secondary: { label: "Book a security review", href: "/request-demo" },
  steps: [
    "30-min walkthrough",
    "Live audit on your model",
    "Audit report delivered",
  ],
  trustLine: "No model data retained \u00b7 Cancel anytime \u00b7 SOC 2 compliant",
};

export const footerLinks = {
  product: [
    { label: "Documentation", href: "/docs" },
    { label: "API Reference", href: "/docs" },
    { label: "Pricing", href: "/pricing" },
    { label: "Changelog", href: "/changelog" },
  ],
  resources: [
    { label: "Blog", href: "/blog" },
    { label: "Guides", href: "/guides" },
    { label: "Case Studies", href: "/case-studies" },
    { label: "Community", href: "/community" },
  ],
  company: [
    { label: "About", href: "/about" },
    { label: "Careers", href: "/careers" },
    { label: "Contact", href: "/contact" },
    { label: "Status", href: "/status" },
  ],
  compliance: [
    { label: "SOC 2", href: "/security" },
    { label: "Privacy Policy", href: "/privacy" },
    { label: "Terms of Service", href: "/terms" },
    { label: "DPA", href: "/dpa" },
  ],
};
