"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api, AssetRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";

interface PaletteAction {
  id: string;
  label: string;
  group: string;
  run: () => void;
}

const STATIC_PAGES: { label: string; href: string }[] = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Assets", href: "/markets/assets" },
  { label: "Options Chain", href: "/markets/options-chain" },
  { label: "Volatility Surface", href: "/markets/volatility-surface" },
  { label: "Forecast Lab", href: "/research/forecast-lab" },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [assets, setAssets] = useState<AssetRead[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const { token } = useAuth();
  const { setSelectedSymbol } = useWorkspaceState();

  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((prev) => !prev);
      }
      if (event.key === "Escape") {
        setOpen(false);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  useEffect(() => {
    if (open && token && assets.length === 0) {
      api.listAssets(token).then(setAssets).catch(() => undefined);
    }
    if (open) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setQuery("");
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [open, token, assets.length]);

  const actions: PaletteAction[] = useMemo(() => {
    const pageActions: PaletteAction[] = STATIC_PAGES.map((page) => ({
      id: `page:${page.href}`,
      label: page.label,
      group: "Navigate",
      run: () => router.push(page.href),
    }));

    const assetActions: PaletteAction[] = assets.map((asset) => ({
      id: `asset:${asset.symbol}`,
      label: `${asset.symbol} — ${asset.name}`,
      group: "Jump to asset",
      run: () => {
        setSelectedSymbol(asset.symbol);
        router.push("/markets/options-chain");
      },
    }));

    return [...pageActions, ...assetActions];
  }, [assets, router, setSelectedSymbol]);

  const filtered = useMemo(() => {
    if (!query.trim()) return actions;
    const needle = query.trim().toLowerCase();
    return actions.filter((a) => a.label.toLowerCase().includes(needle));
  }, [actions, query]);

  const runAction = useCallback(
    (action: PaletteAction) => {
      action.run();
      setOpen(false);
    },
    []
  );

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-ink/70 backdrop-blur-sm"
      onClick={() => setOpen(false)}
    >
      <div
        className="w-full max-w-lg bg-panel border border-line rounded-md shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <input
          ref={inputRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Jump to a page or asset..."
          className="w-full bg-panel-raised px-4 py-3 text-sm text-text-primary outline-none border-b border-line font-mono"
        />
        <div className="max-h-80 overflow-y-auto py-1">
          {filtered.length === 0 ? (
            <p className="px-4 py-6 text-sm text-text-tertiary text-center">No matches</p>
          ) : (
            filtered.map((action) => (
              <button
                key={action.id}
                onClick={() => runAction(action)}
                className="w-full text-left px-4 py-2 text-sm text-text-secondary hover:bg-panel-raised hover:text-text-primary transition-colors flex items-center justify-between"
              >
                <span>{action.label}</span>
                <span className="text-[10px] font-mono uppercase tracking-wide text-text-tertiary">
                  {action.group}
                </span>
              </button>
            ))
          )}
        </div>
        <div className="px-4 py-2 border-t border-line text-[10px] font-mono text-text-tertiary flex items-center gap-3">
          <span>⌘K to toggle</span>
          <span>Esc to close</span>
        </div>
      </div>
    </div>
  );
}
