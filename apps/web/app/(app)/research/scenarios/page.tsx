"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, ScenarioResultRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";

export default function ScenariosPage() {
  const { token } = useAuth();
  const { selectedSymbol, ready } = useWorkspaceState();
  const [spotShock, setSpotShock] = useState(0);
  const [volShock, setVolShock] = useState(0);
  const [result, setResult] = useState<ScenarioResultRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !ready) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);
    api
      .runScenario(token, selectedSymbol, spotShock, volShock)
      .then(setResult)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Failed to run scenario"))
      .finally(() => setLoading(false));
  }, [token, ready, selectedSymbol, spotShock, volShock]);

  return (
    <main className="p-8">
      <header className="mb-6">
        <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
          Research
        </span>
        <h1 className="text-2xl font-semibold text-text-primary mt-1">
          Scenario Lab — {selectedSymbol}
        </h1>
        <p className="text-text-secondary mt-1 text-sm">
          Shock spot and implied volatility, reprice the full chain with Black-Scholes.
        </p>
      </header>

      <section className="bg-panel border border-line rounded-md p-6 mb-6 grid sm:grid-cols-2 gap-6">
        <label className="flex flex-col gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wide text-text-tertiary">
            Spot shock: {(spotShock * 100).toFixed(0)}%
          </span>
          <input
            type="range"
            min={-0.5}
            max={0.5}
            step={0.01}
            value={spotShock}
            onChange={(e) => setSpotShock(Number(e.target.value))}
            className="accent-accent-amber"
          />
        </label>
        <label className="flex flex-col gap-2">
          <span className="text-[10px] font-mono uppercase tracking-wide text-text-tertiary">
            Volatility shock: {(volShock * 100).toFixed(0)}%
          </span>
          <input
            type="range"
            min={-0.5}
            max={1}
            step={0.01}
            value={volShock}
            onChange={(e) => setVolShock(Number(e.target.value))}
            className="accent-accent-cyan"
          />
        </label>
      </section>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading || !result ? (
        <p className="text-sm text-text-secondary">Repricing chain...</p>
      ) : (
        <div className="flex flex-col gap-6">
          <section className="grid sm:grid-cols-3 gap-4">
            <StatCard label="Base spot" value={`$${result.base_spot.toFixed(2)}`} />
            <StatCard label="Shocked spot" value={`$${result.shocked_spot.toFixed(2)}`} />
            <StatCard
              label="Net delta change"
              value={`${(result.total_delta_change_pct * 100).toFixed(1)}%`}
            />
          </section>

          <section className="border border-line rounded-md overflow-hidden overflow-x-auto">
            <table className="w-full text-sm min-w-[720px]">
              <thead>
                <tr className="bg-panel-raised text-text-tertiary text-xs font-mono uppercase tracking-wide">
                  <th className="text-left px-4 py-2.5">Type</th>
                  <th className="text-right px-4 py-2.5">Strike</th>
                  <th className="text-left px-4 py-2.5">Expiry</th>
                  <th className="text-right px-4 py-2.5">Base price</th>
                  <th className="text-right px-4 py-2.5">Shocked price</th>
                  <th className="text-right px-4 py-2.5">Change</th>
                </tr>
              </thead>
              <tbody>
                {result.contracts.slice(0, 40).map((c) => (
                  <tr
                    key={`${c.expiry}-${c.strike}-${c.option_type}`}
                    className="border-t border-line"
                  >
                    <td
                      className={`px-4 py-2 font-mono uppercase text-xs ${
                        c.option_type === "call" ? "text-accent-cyan" : "text-danger"
                      }`}
                    >
                      {c.option_type}
                    </td>
                    <td className="px-4 py-2 text-right font-mono text-text-primary">
                      {c.strike.toFixed(2)}
                    </td>
                    <td className="px-4 py-2 font-mono text-text-secondary">{c.expiry}</td>
                    <td className="px-4 py-2 text-right font-mono text-text-secondary">
                      {c.base_price.toFixed(2)}
                    </td>
                    <td className="px-4 py-2 text-right font-mono text-text-primary">
                      {c.shocked_price.toFixed(2)}
                    </td>
                    <td
                      className={`px-4 py-2 text-right font-mono ${
                        c.price_change_pct >= 0 ? "text-accent-cyan" : "text-danger"
                      }`}
                    >
                      {(c.price_change_pct * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </div>
      )}
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-panel border border-line rounded-md p-4">
      <p className="text-[10px] font-mono uppercase tracking-wide text-text-tertiary mb-1">
        {label}
      </p>
      <p className="text-lg font-mono text-text-primary">{value}</p>
    </div>
  );
}
