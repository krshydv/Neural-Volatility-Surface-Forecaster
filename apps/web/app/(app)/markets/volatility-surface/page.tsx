"use client";

import { useEffect, useMemo, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, VolatilitySurfaceRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";
import { VolSurfaceHeatmap } from "@/components/vol-surface-heatmap";
import { LineChart } from "@/components/line-chart";

const METHODS = ["linear", "cubic", "rbf"];

export default function VolatilitySurfacePage() {
  const { token } = useAuth();
  const { selectedSymbol, ready, surfaceSettings, setSurfaceSettings } = useWorkspaceState();
  const [surface, setSurface] = useState<VolatilitySurfaceRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expiryIndex, setExpiryIndex] = useState(0);

  useEffect(() => {
    if (!token || !ready) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);
    api
      .getVolatilitySurface(token, selectedSymbol, surfaceSettings.method, surfaceSettings.gridResolution)
      .then((data) => {
        setSurface(data);
        setExpiryIndex(Math.floor(data.expiry_grid.length / 2));
      })
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to build volatility surface")
      )
      .finally(() => setLoading(false));
  }, [token, ready, selectedSymbol, surfaceSettings]);

  const atmIndex = useMemo(() => {
    if (!surface) return 0;
    return surface.moneyness_grid.reduce(
      (closest, value, index) =>
        Math.abs(value) < Math.abs(surface.moneyness_grid[closest]) ? index : closest,
      0
    );
  }, [surface]);

  return (
    <main className="p-8">
      <header className="mb-6 flex items-end justify-between flex-wrap gap-4">
        <div>
          <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
            Markets
          </span>
          <h1 className="text-2xl font-semibold text-text-primary mt-1">
            Volatility Surface — {selectedSymbol}
          </h1>
          {surface && (
            <p className="text-text-secondary mt-1 text-sm">
              Spot ${surface.spot.toFixed(2)} · {surface.method} interpolation
            </p>
          )}
        </div>

        <select
          value={surfaceSettings.method}
          onChange={(e) => setSurfaceSettings({ ...surfaceSettings, method: e.target.value })}
          className="bg-panel-raised border border-line rounded-sm px-3 py-1.5 text-sm font-mono text-text-primary outline-none focus:border-accent-amber"
        >
          {METHODS.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </header>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading || !surface ? (
        <p className="text-sm text-text-secondary">Building surface...</p>
      ) : (
        <div className="flex flex-col gap-8">
          <section className="bg-panel border border-line rounded-md p-6">
            <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary mb-4">
              Surface heatmap
            </h2>
            <VolSurfaceHeatmap
              rows={surface.expiry_grid}
              cols={surface.moneyness_grid}
              grid={surface.volatility_grid}
              rowLabel="Expiry (yrs)"
              colLabel="Log-moneyness"
            />
          </section>

          <div className="grid md:grid-cols-2 gap-6">
            <section className="bg-panel border border-line rounded-md p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary">
                  Volatility smile
                </h2>
                <select
                  value={expiryIndex}
                  onChange={(e) => setExpiryIndex(Number(e.target.value))}
                  className="bg-panel-raised border border-line rounded-sm px-2 py-1 text-xs font-mono text-text-primary outline-none"
                >
                  {surface.expiry_grid.map((expiry, index) => (
                    <option key={expiry} value={index}>
                      T = {expiry.toFixed(2)}y
                    </option>
                  ))}
                </select>
              </div>
              <LineChart
                xValues={surface.moneyness_grid}
                series={[
                  {
                    name: "IV",
                    color: "var(--color-accent-amber)",
                    yValues: surface.volatility_grid[expiryIndex],
                  },
                ]}
                xLabel="Log-moneyness"
                yLabel="IV"
                yAsPercent
              />
            </section>

            <section className="bg-panel border border-line rounded-md p-6">
              <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary mb-4">
                Term structure (ATM)
              </h2>
              <LineChart
                xValues={surface.expiry_grid}
                series={[
                  {
                    name: "IV",
                    color: "var(--color-accent-cyan)",
                    yValues: surface.volatility_grid.map((row) => row[atmIndex]),
                  },
                ]}
                xLabel="Expiry (yrs)"
                yLabel="IV"
                yAsPercent
              />
            </section>
          </div>
        </div>
      )}
    </main>
  );
}
