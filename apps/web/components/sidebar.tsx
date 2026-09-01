"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { PulseMark } from "@/components/pulse-mark";
import { useAuth } from "@/lib/auth-context";

const NAV_SECTIONS: { label: string; items: { label: string; href: string }[] }[] = [
  {
    label: "Overview",
    items: [{ label: "Dashboard", href: "/dashboard" }],
  },
  {
    label: "Markets",
    items: [
      { label: "Assets", href: "/markets/assets" },
      { label: "Options Chain", href: "/markets/options-chain" },
      { label: "Volatility Surface", href: "/markets/volatility-surface" },
    ],
  },
  {
    label: "Research",
    items: [
      { label: "Forecast Lab", href: "/research/forecast-lab" },
      { label: "Model Experiments", href: "/research/experiments" },
      { label: "Regime Detection", href: "/research/regime-detection" },
      { label: "Scenarios", href: "/research/scenarios" },
    ],
  },
  {
    label: "Analytics",
    items: [
      { label: "Greeks", href: "/analytics/greeks" },
      { label: "Historical Volatility", href: "/analytics/historical-volatility" },
      { label: "Risk Analytics", href: "/analytics/risk" },
    ],
  },
  {
    label: "Workspace",
    items: [
      { label: "Saved Research", href: "/dashboard" },
      { label: "Data Sources", href: "/workspace/data-sources" },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="w-64 shrink-0 h-screen sticky top-0 flex flex-col bg-primary texture-dots">
      <div className="flex items-center gap-3 px-5 py-5 border-b border-white/15">
        <PulseMark className="h-5 w-16" inverse />
        <span className="label-tag text-text-inverse whitespace-nowrap">
          Hermes Forecast
        </span>
      </div>

      <nav className="flex-1 overflow-y-auto px-3 py-5">
        {NAV_SECTIONS.map((section) => (
          <div key={section.label} className="mb-6">
            <span className="label-chip ml-2 mb-2 inline-block">
              {section.label}
            </span>
            <div className="flex flex-col gap-0.5">
              {section.items.map((item) => {
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`px-2.5 py-1.5 text-sm font-mono transition-colors ${
                      active
                        ? "bg-background text-primary font-medium"
                        : "text-text-inverse-muted border-l-2 border-transparent hover:text-text-inverse hover:bg-white/10"
                    }`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="px-4 py-4 border-t border-white/15">
        <p className="text-sm text-text-inverse font-mono truncate">
          {user?.full_name ?? user?.email}
        </p>
        <button
          onClick={logout}
          className="mt-2 label-tag text-text-inverse-muted hover:text-white transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
