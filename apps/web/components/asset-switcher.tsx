"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, AssetRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";

export function AssetSwitcher() {
  const { token } = useAuth();
  const { selectedSymbol, setSelectedSymbol } = useWorkspaceState();
  const [assets, setAssets] = useState<AssetRead[]>([]);

  useEffect(() => {
    if (!token) return;
    api.listAssets(token).then(setAssets).catch(() => undefined);
  }, [token]);

  return (
    <select
      value={selectedSymbol}
      onChange={(e) => setSelectedSymbol(e.target.value)}
      className="bg-panel-raised border border-line rounded-sm px-3 py-1.5 text-sm font-mono text-text-primary outline-none focus:border-accent-amber"
    >
      {assets.length === 0 && <option value={selectedSymbol}>{selectedSymbol}</option>}
      {assets.map((asset) => (
        <option key={asset.symbol} value={asset.symbol}>
          {asset.symbol} — {asset.name}
        </option>
      ))}
    </select>
  );
}
