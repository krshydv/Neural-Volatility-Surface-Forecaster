"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, RegimeDetectionRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";

const REGIME_COLORS: Record<string, string> = {
  "Low volatility": "var(--color-accent-cyan)",
  "Medium volatility": "var(--color-accent-amber)",
  "High volatility": "var(--color-danger)",
};

export default function RegimeDetectionPage() {
  const { token } = useAuth();
  const { selectedSymbol, ready } = useWorkspaceState();
  const [data, setData] = useState<RegimeDetectionRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !ready) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);
    api
      .getRegimeDetection(token, selectedSymbol)
      .then(setData)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to detect regimes")
      )
      .finally(() => setLoading(false));
  }, [token, ready, selectedSymbol]);

  return (
    <main className="p-8">
      <header className="mb-6">
        <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
          Research
        </span>
        <h1 className="text-2xl font-semibold text-text-primary mt-1">
          Regime Detection — {selectedSymbol}
        </h1>
        <p className="text-text-secondary mt-1 text-sm">
          Unsupervised clustering (k-means over rolling realized volatility) into low / medium /
          high volatility regimes.
        </p>
      </header>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading || !data ? (
        <p className="text-sm text-text-secondary">Clustering volatility history...</p>
      ) : (
        <div className="flex flex-col gap-6">
          <section className="bg-panel border border-line rounded-md p-6 flex items-center gap-4">
            <span
              className="w-3 h-3 rounded-full"
              style={{ background: REGIME_COLORS[data.current_regime] }}
            />
            <div>
              <p className="text-[10px] font-mono uppercase tracking-wide text-text-tertiary">
                Current regime
              </p>
              <p className="text-lg font-mono text-text-primary">{data.current_regime}</p>
            </div>
          </section>

          <section className="bg-panel border border-line rounded-md p-6">
            <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary mb-4">
              Volatility timeline
            </h2>
            <svg viewBox="0 0 640 200" className="w-full max-w-3xl">
              {data.points.map((p, i) => {
                const maxVol = Math.max(...data.points.map((d) => d.realized_vol));
                const barWidth = 640 / data.points.length;
                const barHeight = (p.realized_vol / maxVol) * 160;
                return (
                  <rect
                    key={p.trade_date}
                    x={i * barWidth}
                    y={180 - barHeight}
                    width={Math.max(barWidth - 1, 1)}
                    height={barHeight}
                    fill={REGIME_COLORS[p.regime_label]}
                  >
                    <title>{`${p.trade_date}: ${(p.realized_vol * 100).toFixed(1)}% (${p.regime_label})`}</title>
                  </rect>
                );
              })}
            </svg>
            <div className="flex gap-4 mt-3">
              {Object.entries(REGIME_COLORS).map(([label, color]) => (
                <div key={label} className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full" style={{ background: color }} />
                  <span className="text-[10px] font-mono text-text-tertiary">{label}</span>
                </div>
              ))}
            </div>
          </section>

          <section className="bg-panel border border-line rounded-md p-6">
            <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary mb-4">
              Cluster centroids (annualized realized vol)
            </h2>
            <div className="flex gap-6">
              {data.centroids.map((c, i) => (
                <div key={i}>
                  <p className="text-[10px] font-mono uppercase text-text-tertiary">
                    {["Low", "Medium", "High"][i]}
                  </p>
                  <p className="font-mono text-text-primary">{(c * 100).toFixed(1)}%</p>
                </div>
              ))}
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
