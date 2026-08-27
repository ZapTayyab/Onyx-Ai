"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  FlaskConical,
  GitBranch,
  Bell,
  FileText,
  Settings,
  Shield,
  ChevronLeft,
  ChevronDown,
  Users,
  CreditCard,
  Bot,
  Layers,
} from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/evaluations", label: "Evaluations", icon: FlaskConical },
  { href: "/traces", label: "Traces", icon: GitBranch },
  { href: "/alerts", label: "Alerts", icon: Bell },
  { href: "/reports", label: "Reports", icon: FileText },
  { href: "/agents", label: "Agents", icon: Bot },
  { href: "/suites", label: "Suites", icon: Layers },
  {
    label: "Settings",
    icon: Settings,
    children: [
      { href: "/settings", label: "General", icon: Settings },
      { href: "/settings/team", label: "Team", icon: Users },
      { href: "/settings/billing", label: "Billing", icon: CreditCard },
    ],
  },
];

function NavItem({
  item,
  collapsed,
  pathname,
  index,
}: {
  item: (typeof navItems)[number];
  collapsed: boolean;
  pathname: string;
  index: number;
}) {
  const [submenuOpen, setSubmenuOpen] = useState(false);
  const isActive = "href" in item && !("children" in item)
    ? pathname === item.href
    : false;
  const isChildActive =
    "children" in item && item.children
      ? item.children.some((c) => pathname === c.href || pathname.startsWith(c.href + "/"))
      : false;

  useEffect(() => {
    if (isChildActive) setSubmenuOpen(true);
  }, [isChildActive]);

  if ("children" in item && item.children) {
    return (
      <div
        className="animate-fade-in"
        style={{ animationDelay: `${index * 50}ms`, opacity: 0 }}
      >
        <button
          onClick={() => {
            if (collapsed) return;
            setSubmenuOpen(!submenuOpen);
          }}
          className={cn(
            "group relative flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all duration-200",
            isChildActive
              ? "bg-primary/10 text-primary"
              : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
          )}
        >
          <item.icon className="h-5 w-5 shrink-0 transition-transform duration-200 group-hover:scale-110" />
          {!collapsed && (
            <>
              <span className="flex-1 text-left">{item.label}</span>
              <ChevronDown
                className={cn(
                  "h-4 w-4 transition-all duration-200",
                  submenuOpen && "rotate-180"
                )}
              />
            </>
          )}
        </button>
        <div
          className={cn(
            "grid transition-all duration-300 ease-in-out",
            submenuOpen && !collapsed
              ? "grid-rows-[1fr] opacity-100"
              : "grid-rows-[0fr] opacity-0"
          )}
        >
          <div className="overflow-hidden">
            <div className="ml-2 mt-1 space-y-1">
              {item.children.map((child) => {
                const isChildActive = pathname === child.href;
                return (
                  <Link
                    key={child.href}
                    href={child.href}
                    className={cn(
                      "relative flex items-center gap-3 rounded-md px-3 py-1.5 text-sm transition-all duration-200",
                      isChildActive
                        ? "bg-primary/5 text-primary font-medium"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                    )}
                  >
                    <child.icon className="h-4 w-4 shrink-0" />
                    <span className="animate-fade-in-right" style={{ animationDelay: "50ms", opacity: 0 }}>
                      {child.label}
                    </span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <Link
      href={item.href!}
      className="animate-fade-in group relative block"
      style={{ animationDelay: `${index * 50}ms`, opacity: 0 }}
    >
      <div
        className={cn(
          "relative flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-all duration-200",
          isActive
            ? "bg-primary/10 text-primary"
            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        )}
      >
        {isActive && (
          <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-primary animate-scale-in" />
        )}
        <item.icon className="h-5 w-5 shrink-0 transition-transform duration-200 group-hover:scale-110" />
        {!collapsed && (
          <span className="animate-fade-in-right" style={{ animationDelay: "50ms", opacity: 0 }}>
            {item.label}
          </span>
        )}
      </div>
    </Link>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [toggling, setToggling] = useState(false);
  const toggleTimer = useRef<ReturnType<typeof setTimeout>>();

  function handleToggle() {
    setToggling(true);
    setCollapsed(!collapsed);
    clearTimeout(toggleTimer.current);
    toggleTimer.current = setTimeout(() => setToggling(false), 400);
  }

  return (
    <aside
      className={cn(
        "flex flex-col border-r bg-card animate-slide-in-left transition-all duration-300 ease-in-out relative",
        collapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex items-center gap-2 p-4 overflow-hidden">
        <Shield className="h-6 w-6 shrink-0 text-primary transition-transform duration-200" />
        {!collapsed && (
          <span className="font-bold text-lg tracking-tight animate-fade-in-right" style={{ animationDelay: "100ms", opacity: 0 }}>
            Onyx
          </span>
        )}
      </div>
      <Separator />
      <nav className="flex-1 space-y-1 p-2 overflow-x-hidden">
        {navItems.map((item, i) => (
          <NavItem
            key={item.label}
            item={item}
            collapsed={collapsed}
            pathname={pathname}
            index={i}
          />
        ))}
      </nav>
      <Separator />
      <div className="p-2">
        <Button
          variant="ghost"
          size="sm"
          className={cn(
            "w-full justify-center transition-all duration-200",
            toggling && "scale-90"
          )}
          onClick={handleToggle}
        >
          <ChevronLeft
            className={cn(
              "h-4 w-4 transition-all duration-300 ease-in-out",
              collapsed && "rotate-180",
              toggling && "scale-110"
            )}
          />
        </Button>
      </div>
    </aside>
  );
}
