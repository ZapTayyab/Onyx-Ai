import { siteConfig, footerLinks } from "@/lib/landing-content";
import { Shield } from "lucide-react";

export function Footer() {
  const groups = [
    { title: "Product", links: footerLinks.product },
    { title: "Resources", links: footerLinks.resources },
    { title: "Company", links: footerLinks.company },
    { title: "Compliance", links: footerLinks.compliance },
  ];

  return (
    <footer className="border-t border-slate-200 bg-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-16">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-1">
            <a href="/" className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              <span className="text-sm font-semibold text-slate-900">Onyx</span>
            </a>
            <p className="mt-2 text-xs text-slate-500 max-w-xs leading-relaxed">
              {siteConfig.tagline}
            </p>
          </div>
          {groups.map((group) => (
            <div key={group.title}>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
                {group.title}
              </p>
              <ul className="space-y-2">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-slate-500 transition-colors hover:text-slate-900"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
        <div className="mt-16 border-t border-slate-200 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-400">
            &copy; {new Date().getFullYear()} {siteConfig.name} Assurance Platform. Proprietary. All rights reserved.
          </p>
          <p className="text-xs text-slate-400">
            Built for enterprise AI assurance.
          </p>
        </div>
      </div>
    </footer>
  );
}
