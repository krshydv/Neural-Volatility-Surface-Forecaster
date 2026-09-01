"use client";

import { AssetSwitcher } from "@/components/asset-switcher";

export function TopBar() {
  return (
    <div className="flex items-center justify-between px-8 py-3 border-b border-border bg-surface">
      <AssetSwitcher />
      <button
        onClick={() => window.dispatchEvent(new KeyboardEvent("keydown", { key: "k", metaKey: true }))}
        className="label-tag text-text-muted hover:text-text-secondary transition-colors border border-border px-2.5 py-1.5"
      >
        ⌘K search
      </button>
    </div>
  );
}
