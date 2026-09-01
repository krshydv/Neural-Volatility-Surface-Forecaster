"use client";

import { useWorkspaceState } from "@/lib/workspace-state-context";

export default function ExperimentsPage() {
  const { experimentLog } = useWorkspaceState();

  return (
    <main className="p-8">
      <header className="mb-6">
        <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
          Research
        </span>
        <h1 className="text-2xl font-semibold text-text-primary mt-1">Model Experiments</h1>
        <p className="text-text-secondary mt-1 text-sm">
          A running log of forecast runs from the Forecast Lab, persisted to this workspace so you
          can compare configurations over time.
        </p>
      </header>

      {experimentLog.length === 0 ? (
        <p className="text-sm text-text-secondary">
          No runs logged yet — run a forecast in the Forecast Lab to see it appear here.
        </p>
      ) : (
        <div className="border border-line rounded-md overflow-hidden overflow-x-auto">
          <table className="w-full text-sm min-w-[640px]">
            <thead>
              <tr className="bg-panel-raised text-text-tertiary text-xs font-mono uppercase tracking-wide">
                <th className="text-left px-4 py-2.5">Ran at</th>
                <th className="text-left px-4 py-2.5">Symbol</th>
                <th className="text-left px-4 py-2.5">Model</th>
                <th className="text-right px-4 py-2.5">Horizon</th>
                <th className="text-right px-4 py-2.5">Epochs</th>
                <th className="text-right px-4 py-2.5">Train loss</th>
                <th className="text-right px-4 py-2.5">MAE</th>
              </tr>
            </thead>
            <tbody>
              {experimentLog.map((run, i) => (
                <tr key={`${run.ranAt}-${i}`} className="border-t border-line">
                  <td className="px-4 py-2 font-mono text-text-tertiary">
                    {new Date(run.ranAt).toLocaleString()}
                  </td>
                  <td className="px-4 py-2 font-mono text-accent-amber">{run.symbol}</td>
                  <td className="px-4 py-2 font-mono text-text-secondary uppercase">
                    {run.modelType ?? "mlp"}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-secondary">
                    {run.horizonDays}d
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-secondary">
                    {run.epochs}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-secondary">
                    {run.finalTrainLoss.toFixed(4)}
                  </td>
                  <td className="px-4 py-2 text-right font-mono text-text-primary">
                    {(run.meanAbsoluteError * 100).toFixed(2)}%
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
