"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, RiskExposureRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";

export default function RiskAnalyticsPage() {
  const { token } = useAuth();
  const { selectedSymbol, ready } = useWorkspaceState();
  const [data, setData] = useState<RiskExposureRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !ready) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);
    api
      .getRiskExposure(token, selectedSymbol)
      .then(setData)
      .catch((err) =>
        setError(err instanceof ApiError ? err.message : "Failed to compute risk exposure")
      )
      .finally(() => setLoading(false));
  }, [token, ready, selectedSymbol]);

  return (
    <main className="p-8 max-w-3xl">
      <header className="mb-6">
        <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
          Analytics
        </span>
        <h1 className="text-2xl font-semibold text-text-primary mt-1">
          Risk Analytics — {selectedSymbol}
        </h1>
        <p className="text-text-secondary mt-1 text-sm">
          Net Greeks exposure aggregated across the full options chain.
        </p>
      </header>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading || !data ? (
        <p className="text-sm text-text-secondary">Aggregating exposure...</p>
      ) : (
        <div className="grid sm:grid-cols-2 gap-4">
          <StatCard label="Spot" value={`$${data.spot.toFixed(2)}`} />
          <StatCard label="Contracts" value={data.contract_count.toString()} />
          <StatCard label="Net delta" value={data.net_delta.toFixed(2)} />
          <StatCard label="Net gamma" value={data.net_gamma.toFixed(4)} />
          <StatCard label="Net vega" value={data.net_vega.toFixed(2)} />
          <StatCard label="Net theta" value={data.net_theta.toFixed(2)} />
          <StatCard
            label="OI-weighted delta"
            value={data.open_interest_weighted_delta.toFixed(0)}
          />
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
