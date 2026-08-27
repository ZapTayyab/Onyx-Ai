"use client";

import { useState, useEffect } from "react";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Shield, Menu, X } from "lucide-react";
import { siteConfig, navLinks } from "@/lib/landing-content";

export function Header() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const pathname = usePathname();
  const isHome = pathname === "/";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const hashToPath: Record<string, string> = {
    "#product": "/",
    "#docs": "/docs",
    "#pricing": "/pricing",
    "#blog": "/blog",
  };

  const resolveHref = (href: string) => {
    if (href.startsWith("#") && !isHome) {
      return hashToPath[href] || `/${href}`;
    }
    return href;
  };

  return (
    <header
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
        scrolled
          ? "bg-white/90 backdrop-blur-xl border-b border-slate-200"
          : "bg-transparent"
      )}
    >
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <a href="/" className="flex items-center gap-2.5">
          <Shield className={cn("h-6 w-6 transition-colors", scrolled ? "text-blue-600" : "text-blue-600")} />
          <span className={cn("text-base font-semibold tracking-tight transition-colors", scrolled ? "text-slate-900" : "text-slate-900")}>
            {siteConfig.name}
          </span>
        </a>

        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.label}
              href={resolveHref(link.href)}
              className={
                link.variant === "primary"
                  ? "inline-flex h-9 items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-medium text-white transition-all hover:bg-blue-500 hover:shadow-[0_0_20px_-5px] hover:shadow-blue-500/40"
                  : link.variant === "ghost"
                  ? "text-sm text-slate-600 transition-colors hover:text-slate-900"
                  : "text-sm text-slate-600 transition-colors hover:text-slate-900"
              }
            >
              {link.label}
            </a>
          ))}
        </nav>

        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="md:hidden text-slate-600 hover:text-slate-900 transition-colors"
          aria-label="Toggle menu"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white/95 backdrop-blur-xl">
          <nav className="flex flex-col gap-2 px-6 py-4">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={resolveHref(link.href)}
                onClick={() => setMobileOpen(false)}
                className={
                  link.variant === "primary"
                    ? "inline-flex h-9 items-center justify-center rounded-md bg-blue-600 px-4 text-sm font-medium text-white"
                    : "py-2 text-sm text-slate-600 transition-colors hover:text-slate-900"
                }
              >
                {link.label}
              </a>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
