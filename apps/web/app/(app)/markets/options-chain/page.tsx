"use client";

import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, OptionsChainRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";

export default function OptionsChainPage() {
  const { token } = useAuth();
  const { selectedSymbol, ready } = useWorkspaceState();
  const [chain, setChain] = useState<OptionsChainRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expiryFilter, setExpiryFilter] = useState<string>("all");

  useEffect(() => {
    if (!token || !ready) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);
    api
      .getOptionsChain(token, selectedSymbol)
      .then((data) => {
        setChain(data);
        setExpiryFilter("all");
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to load chain"))
      .finally(() => setLoading(false));
  }, [token, ready, selectedSymbol]);

  const expiries = useMemo(() => {
    if (!chain) return [];
    return Array.from(new Set(chain.contracts.map((c) => c.expiry))).sort();
  }, [chain]);

  const rows = useMemo(() => {
    if (!chain) return [];
    return chain.contracts
      .filter((c) => expiryFilter === "all" || c.expiry === expiryFilter)
      .sort((a, b) => a.expiry.localeCompare(b.expiry) || a.strike - b.strike);
  }, [chain, expiryFilter]);

  return (
    <main className="p-8">
      <header className="mb-6 flex items-end justify-between">
        <div>
          <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
            Markets
          </span>
          <h1 className="text-2xl font-semibold text-text-primary mt-1">
            Options Chain — {selectedSymbol}
          </h1>
          {chain && (
            <p className="text-text-secondary mt-1 text-sm">
              Spot ${chain.spot.toFixed(2)} · as of {new Date(chain.as_of).toLocaleString()}
            </p>
          )}
        </div>

        {expiries.length > 0 && (
          <select
            value={expiryFilter}
            onChange={(e) => setExpiryFilter(e.target.value)}
            className="bg-panel-raised border border-line rounded-sm px-3 py-1.5 text-sm font-mono text-text-primary outline-none focus:border-accent-amber"
          >
            <option value="all">All expiries</option>
            {expiries.map((expiry) => (
              <option key={expiry} value={expiry}>
                {expiry}
              </option>
            ))}
          </select>
        )}
      </header>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading ? (
        <p className="text-sm text-text-secondary">Loading options chain...</p>
      ) : (
        <div className="border border-line rounded-md overflow-hidden overflow-x-auto">
          <table className="w-full text-sm min-w-[720px]">
            <thead>
              <tr className="bg-panel-raised text-text-tertiary text-xs font-mono uppercase tracking-wide">
                <th className="text-left px-4 py-2.5">Type</th>
                <th className="text-left px-4 py-2.5">Expiry</th>
                <th className="text-right px-4 py-2.5">Strike</th>
                <th className="text-right px-4 py-2.5">Bid</th>
                <th className="text-right px-4 py-2.5">Ask</th>
                <th className="text-right px-4 py-2.5">Last</th>
                <th className="text-right px-4 py-2.5">IV</th>
                <th className="text-right px-4 py-2.5">OI</th>
                <th className="text-right px-4 py-2.5">Vol</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((c) => (
                <tr
                  key={`${c.expiry}-${c.strike}-${c.option_type}`}
                  className="border-t border-line hover:bg-panel-raised transition-colors"
                >
                  <td
                    className={`px-4 py-2 font-mono uppercase text-xs ${
                      c.option_type === "call" ? "text-accent-cyan" : "text-danger"
                    }`}
                  >
                    {c.option_type}
                  </td>
                  <td className="px-4 py-2 font-mono text-text-secondary">{c.expiry}</td>
                  <td className="px-4 py-2 text-right font-mono text-text-primary">
                    {c.strike.toFixed(2)}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-secondary">
                    {c.bid.toFixed(2)}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-secondary">
                    {c.ask.toFixed(2)}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-primary">
                    {c.last.toFixed(2)}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-accent-amber">
                    {(c.implied_volatility * 100).toFixed(1)}%
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-tertiary">
                    {c.open_interest}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-tertiary">{c.volume}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
