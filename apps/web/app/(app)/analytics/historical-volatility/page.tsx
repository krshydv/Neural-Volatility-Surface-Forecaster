"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, PricePointRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";
import { LineChart } from "@/components/line-chart";

export default function HistoricalVolatilityPage() {
  const { token } = useAuth();
  const { selectedSymbol, ready } = useWorkspaceState();
  const [prices, setPrices] = useState<PricePointRead[]>([]);
  const [realizedVol, setRealizedVol] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(180);

  useEffect(() => {
    if (!token || !ready) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);
    api
      .getAssetPrices(token, selectedSymbol, days)
      .then(async (data) => {
        setPrices(data);
        const closes = data.map((p) => p.close);
        const result = await api.getHistoricalVolatility(token, closes);
        setRealizedVol(result.realized_volatility);
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to compute historical volatility")
      )
      .finally(() => setLoading(false));
  }, [token, ready, selectedSymbol, days]);

  return (
    <main className="p-8">
      <header className="mb-6 flex items-end justify-between flex-wrap gap-4">
        <div>
          <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
            Analytics
          </span>
          <h1 className="text-2xl font-semibold text-text-primary mt-1">
            Historical Volatility — {selectedSymbol}
          </h1>
        </div>
        <select
          value={days}
          onChange={(e) => setDays(Number(e.target.value))}
          className="bg-panel-raised border border-line rounded-sm px-3 py-1.5 text-sm font-mono text-text-primary outline-none focus:border-accent-amber"
        >
          <option value={60}>60 days</option>
          <option value={180}>180 days</option>
          <option value={365}>365 days</option>
        </select>
      </header>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading ? (
        <p className="text-sm text-text-secondary">Loading price history...</p>
      ) : (
        <div className="flex flex-col gap-6">
          {realizedVol !== null && (
            <section className="bg-panel border border-line rounded-md p-4 inline-flex flex-col w-fit">
              <p className="text-[10px] font-mono uppercase tracking-wide text-text-tertiary mb-1">
                Annualized realized volatility
              </p>
              <p className="text-2xl font-mono text-accent-amber">
                {(realizedVol * 100).toFixed(2)}%
              </p>
            </section>
          )}

          <section className="bg-panel border border-line rounded-md p-6">
            <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary mb-4">
              Price history
            </h2>
            <LineChart
              xValues={prices.map((_, i) => i)}
              series={[
                {
                  name: "Close",
                  color: "var(--color-accent-amber)",
                  yValues: prices.map((p) => p.close),
                },
              ]}
              xLabel="Trading days"
              yLabel="Price"
            />
          </section>
        </div>
      )}
    </main>
  );
}
