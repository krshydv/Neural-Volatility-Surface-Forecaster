"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, AssetRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";
import { useRouter } from "next/navigation";

export default function AssetsPage() {
  const { token } = useAuth();
  const { setSelectedSymbol } = useWorkspaceState();
  const router = useRouter();
  const [assets, setAssets] = useState<AssetRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    api
      .listAssets(token)
      .then(setAssets)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load assets"))
      .finally(() => setLoading(false));
  }, [token]);

  function openAsset(symbol: string) {
    setSelectedSymbol(symbol);
    router.push("/markets/options-chain");
  }

  return (
    <main className="p-8 max-w-4xl">
      <header className="mb-8">
        <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
          Markets
        </span>
        <h1 className="text-2xl font-semibold text-text-primary mt-1">Assets</h1>
        <p className="text-text-secondary mt-1 text-sm">
          Instruments served by the configured market data provider.
        </p>
      </header>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading ? (
        <p className="text-sm text-text-secondary">Loading assets...</p>
      ) : (
        <div className="border border-line rounded-md overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-panel-raised text-text-tertiary text-xs font-mono uppercase tracking-wide">
                <th className="text-left px-4 py-2.5">Symbol</th>
                <th className="text-left px-4 py-2.5">Name</th>
                <th className="text-left px-4 py-2.5">Class</th>
                <th className="text-right px-4 py-2.5">Last Price</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset) => (
                <tr
                  key={asset.symbol}
                  onClick={() => openAsset(asset.symbol)}
                  className="border-t border-line hover:bg-panel-raised cursor-pointer transition-colors"
                >
                  <td className="px-4 py-2.5 font-mono text-accent-amber">{asset.symbol}</td>
                  <td className="px-4 py-2.5 text-text-primary">{asset.name}</td>
                  <td className="px-4 py-2.5 text-text-secondary capitalize">{asset.asset_class}</td>
                  <td className="px-4 py-2.5 text-right font-mono text-text-primary">
                    ${asset.last_price.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
