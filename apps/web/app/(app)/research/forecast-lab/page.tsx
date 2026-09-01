"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, VolatilityForecastRead } from "@/lib/api";
import { useWorkspaceState } from "@/lib/workspace-state-context";
import { LineChart } from "@/components/line-chart";
import type { ForecastModelType } from "@/lib/api";

const HORIZON_OPTIONS = [5, 10, 20];
const MODEL_OPTIONS: { value: ForecastModelType; label: string }[] = [
  { value: "lstm", label: "LSTM (from-scratch)" },
  { value: "mlp", label: "MLP (baseline)" },
];

export default function ForecastLabPage() {
  const { token } = useAuth();
  const { selectedSymbol, ready, appendExperiment } = useWorkspaceState();
  const [horizon, setHorizon] = useState(10);
  const [modelType, setModelType] = useState<ForecastModelType>("lstm");
  const [forecast, setForecast] = useState<VolatilityForecastRead | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !ready) return;
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true);
    setError(null);
    api
      .getForecast(token, selectedSymbol, horizon, 400, modelType)
      .then((data) => {
        setForecast(data);
        appendExperiment({
          symbol: data.symbol,
          modelType: data.model_type,
          horizonDays: data.horizon_days,
          epochs: data.epochs,
          meanAbsoluteError: data.mean_absolute_error,
          finalTrainLoss: data.final_train_loss,
          ranAt: new Date().toISOString(),
        });
      })
      .catch((err) =>
        setError(
          err instanceof ApiError
            ? err.message
            : "Failed to run forecast — this symbol may not have enough history yet"
        )
      )
      .finally(() => setLoading(false));
  }, [token, ready, selectedSymbol, horizon, modelType, appendExperiment]);

  return (
    <main className="p-8">
      <header className="mb-6 flex items-end justify-between flex-wrap gap-4">
        <div>
          <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
            Research
          </span>
          <h1 className="text-2xl font-semibold text-text-primary mt-1">
            Forecast Lab — {selectedSymbol}
          </h1>
          <p className="text-text-secondary mt-1 text-sm">
            A small neural network trained live on realized volatility history, forecasting
            forward with widening confidence bands.
          </p>
        </div>

        <div className="flex gap-3">
          <select
            value={modelType}
            onChange={(e) => setModelType(e.target.value as ForecastModelType)}
            className="bg-panel-raised border border-line rounded-sm px-3 py-1.5 text-sm font-mono text-text-primary outline-none focus:border-accent-amber"
          >
            {MODEL_OPTIONS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
          <select
            value={horizon}
            onChange={(e) => setHorizon(Number(e.target.value))}
            className="bg-panel-raised border border-line rounded-sm px-3 py-1.5 text-sm font-mono text-text-primary outline-none focus:border-accent-amber"
          >
            {HORIZON_OPTIONS.map((h) => (
              <option key={h} value={h}>
                {h}-day horizon
              </option>
            ))}
          </select>
        </div>
      </header>

      {error && <p className="text-sm text-danger mb-4">{error}</p>}

      {loading || !forecast ? (
        <p className="text-sm text-text-secondary">Training model and forecasting...</p>
      ) : (
        <div className="flex flex-col gap-6">
          <section className="bg-panel border border-line rounded-md p-6">
            <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary mb-4">
              Forecasted realized volatility
            </h2>
            <LineChart
              xValues={forecast.points.map((_, i) => i)}
              series={[
                {
                  name: "Forecast",
                  color: "var(--color-accent-amber)",
                  yValues: forecast.points.map((p) => p.volatility),
                },
                {
                  name: "Upper",
                  color: "var(--color-text-tertiary)",
                  yValues: forecast.points.map((p) => p.upper_bound),
                },
                {
                  name: "Lower",
                  color: "var(--color-text-tertiary)",
                  yValues: forecast.points.map((p) => p.lower_bound),
                },
              ]}
              xLabel="Days ahead"
              yLabel="Volatility"
              yAsPercent
            />
          </section>

          <section className="grid sm:grid-cols-5 gap-4">
            <StatCard label="Model" value={forecast.model_type.toUpperCase()} />
            <StatCard label="Training observations" value={forecast.trained_on_observations.toString()} />
            <StatCard label="Epochs" value={forecast.epochs.toString()} />
            <StatCard label="Final train loss" value={forecast.final_train_loss.toFixed(4)} />
            <StatCard label="Mean absolute error" value={(forecast.mean_absolute_error * 100).toFixed(2) + "%"} />
          </section>

          <section className="bg-panel border border-line rounded-md p-6">
            <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary mb-4">
              Forecast detail
            </h2>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-text-tertiary text-xs font-mono uppercase tracking-wide">
                  <th className="text-left py-1.5">Date</th>
                  <th className="text-right py-1.5">Volatility</th>
                  <th className="text-right py-1.5">Lower</th>
                  <th className="text-right py-1.5">Upper</th>
                </tr>
              </thead>
              <tbody>
                {forecast.points.map((p) => (
                  <tr key={p.forecast_date} className="border-t border-line">
                    <td className="py-1.5 font-mono text-text-secondary">{p.forecast_date}</td>
                    <td className="py-1.5 text-right font-mono text-accent-amber">
                      {(p.volatility * 100).toFixed(2)}%
                    </td>
                    <td className="py-1.5 text-right font-mono text-text-tertiary">
                      {(p.lower_bound * 100).toFixed(2)}%
                    </td>
                    <td className="py-1.5 text-right font-mono text-text-tertiary">
                      {(p.upper_bound * 100).toFixed(2)}%
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
