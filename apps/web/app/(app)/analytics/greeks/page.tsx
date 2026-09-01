"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, ApiError, OptionPricingResult } from "@/lib/api";

const GREEK_ORDER = ["delta", "gamma", "theta", "vega", "rho"];

export default function GreeksPage() {
  const { token } = useAuth();
  const [inputs, setInputs] = useState({
    spot: 100,
    strike: 100,
    time_to_expiry: 0.5,
    risk_free_rate: 0.045,
    volatility: 0.25,
    dividend_yield: 0,
  });
  const [result, setResult] = useState<OptionPricingResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function update(field: keyof typeof inputs, value: string) {
    setInputs((prev) => ({ ...prev, [field]: Number(value) }));
  }

  async function calculate() {
    if (!token) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.priceOption(token, inputs);
      setResult(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to price option");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-8 max-w-3xl">
      <header className="mb-6">
        <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
          Analytics
        </span>
        <h1 className="text-2xl font-semibold text-text-primary mt-1">Greeks Calculator</h1>
        <p className="text-text-secondary mt-1 text-sm">
          Black-Scholes pricing and Greeks for a single option.
        </p>
      </header>

      <section className="bg-panel border border-line rounded-md p-6 mb-6 grid sm:grid-cols-3 gap-4">
        <Field label="Spot" value={inputs.spot} onChange={(v) => update("spot", v)} />
        <Field label="Strike" value={inputs.strike} onChange={(v) => update("strike", v)} />
        <Field
          label="Time to expiry (yrs)"
          value={inputs.time_to_expiry}
          step={0.05}
          onChange={(v) => update("time_to_expiry", v)}
        />
        <Field
          label="Risk-free rate"
          value={inputs.risk_free_rate}
          step={0.005}
          onChange={(v) => update("risk_free_rate", v)}
        />
        <Field
          label="Volatility"
          value={inputs.volatility}
          step={0.01}
          onChange={(v) => update("volatility", v)}
        />
        <Field
          label="Dividend yield"
          value={inputs.dividend_yield}
          step={0.005}
          onChange={(v) => update("dividend_yield", v)}
        />
      </section>

      <button
        onClick={calculate}
        disabled={loading}
        className="bg-accent-amber text-ink font-mono text-sm px-4 py-2 rounded-sm hover:opacity-90 transition-opacity disabled:opacity-50"
      >
        {loading ? "Calculating..." : "Calculate"}
      </button>

      {error && <p className="text-sm text-danger mt-4">{error}</p>}

      {result && (
        <div className="grid sm:grid-cols-2 gap-6 mt-6">
          <section className="bg-panel border border-line rounded-md p-6">
            <h2 className="text-sm font-mono uppercase tracking-wide text-accent-cyan mb-3">
              Call
            </h2>
            <p className="font-mono text-2xl text-text-primary mb-4">
              ${result.call_price.toFixed(2)}
            </p>
            {GREEK_ORDER.map((g) => (
              <div key={g} className="flex justify-between text-sm py-1 border-t border-line">
                <span className="text-text-tertiary font-mono uppercase">{g}</span>
                <span className="font-mono text-text-primary">
                  {result.call_greeks[g]?.toFixed(4)}
                </span>
              </div>
            ))}
          </section>

          <section className="bg-panel border border-line rounded-md p-6">
            <h2 className="text-sm font-mono uppercase tracking-wide text-danger mb-3">Put</h2>
            <p className="font-mono text-2xl text-text-primary mb-4">
              ${result.put_price.toFixed(2)}
            </p>
            {GREEK_ORDER.map((g) => (
              <div key={g} className="flex justify-between text-sm py-1 border-t border-line">
                <span className="text-text-tertiary font-mono uppercase">{g}</span>
                <span className="font-mono text-text-primary">
                  {result.put_greeks[g]?.toFixed(4)}
                </span>
              </div>
            ))}
          </section>
        </div>
      )}
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  step = 1,
}: {
  label: string;
  value: number;
  onChange: (v: string) => void;
  step?: number;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[10px] font-mono uppercase tracking-wide text-text-tertiary">
        {label}
      </span>
      <input
        type="number"
        step={step}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="bg-panel-raised border border-line rounded-sm px-3 py-1.5 text-sm font-mono text-text-primary outline-none focus:border-accent-amber"
      />
    </label>
  );
}
