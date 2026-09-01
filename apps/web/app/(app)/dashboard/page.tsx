"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { api, WorkspaceRead, ApiError } from "@/lib/api";

export default function DashboardPage() {
  const { token, user } = useAuth();
  const [workspaces, setWorkspaces] = useState<WorkspaceRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [creating, setCreating] = useState(false);

  const loadWorkspaces = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await api.listWorkspaces(token);
      setWorkspaces(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load workspaces");
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    void loadWorkspaces();
  }, [loadWorkspaces]);

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    if (!token || !name.trim()) return;
    setCreating(true);
    setError(null);
    try {
      await api.createWorkspace(token, name.trim());
      setName("");
      await loadWorkspaces();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to create workspace");
    } finally {
      setCreating(false);
    }
  }

  async function handleDelete(id: string) {
    if (!token) return;
    await api.deleteWorkspace(token, id);
    await loadWorkspaces();
  }

  return (
    <main className="p-8 max-w-4xl">
      <header className="mb-8">
        <span className="font-mono text-xs tracking-[0.2em] text-accent-amber uppercase">
          Overview
        </span>
        <h1 className="text-2xl font-semibold text-text-primary mt-1">
          Welcome back, {user?.full_name ?? user?.email}
        </h1>
        <p className="text-text-secondary mt-1 text-sm">
          Your research workspaces persist in Postgres across sessions.
        </p>
      </header>

      <section className="bg-panel border border-line rounded-md p-6 mb-6">
        <h2 className="text-sm font-mono uppercase tracking-wide text-text-secondary mb-4">
          Saved research
        </h2>

        <form onSubmit={handleCreate} className="flex gap-2 mb-6">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. AAPL Earnings Volatility"
            className="flex-1 bg-panel-raised border border-line rounded-sm px-3 py-2 text-sm text-text-primary focus:border-accent-amber outline-none"
          />
          <button
            type="submit"
            disabled={creating || !name.trim()}
            className="bg-accent-amber text-ink font-medium rounded-sm px-4 py-2 text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            New workspace
          </button>
        </form>

        {error && <p className="text-sm text-danger mb-4">{error}</p>}

        {loading ? (
          <p className="text-sm text-text-secondary">Loading workspaces...</p>
        ) : workspaces.length === 0 ? (
          <p className="text-sm text-text-secondary">
            No workspaces yet. Create one above to start tracking research.
          </p>
        ) : (
          <ul className="flex flex-col gap-2">
            {workspaces.map((ws) => (
              <li
                key={ws.id}
                className="flex items-center justify-between bg-panel-raised border border-line rounded-sm px-4 py-3"
              >
                <div>
                  <p className="text-sm text-text-primary">{ws.name}</p>
                  <p className="text-xs text-text-tertiary font-mono">
                    Created {new Date(ws.created_at).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(ws.id)}
                  className="text-xs font-mono text-text-secondary hover:text-danger transition-colors"
                >
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}
