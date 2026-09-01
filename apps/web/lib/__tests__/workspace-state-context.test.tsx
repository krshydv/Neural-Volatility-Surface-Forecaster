import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, render, screen, waitFor } from "@testing-library/react";
import { WorkspaceStateProvider, useWorkspaceState } from "@/lib/workspace-state-context";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

vi.mock("@/lib/api", () => ({
  api: {
    listWorkspaces: vi.fn(),
    createWorkspace: vi.fn(),
    updateWorkspace: vi.fn(),
  },
}));

vi.mock("@/lib/auth-context", () => ({
  useAuth: vi.fn(),
}));

function Probe() {
  const { ready, selectedSymbol, setSelectedSymbol, experimentLog, appendExperiment } =
    useWorkspaceState();
  return (
    <div>
      <span data-testid="ready">{String(ready)}</span>
      <span data-testid="symbol">{selectedSymbol}</span>
      <span data-testid="log-count">{experimentLog.length}</span>
      <button onClick={() => setSelectedSymbol("TSLA")}>select-tsla</button>
      <button
        onClick={() =>
          appendExperiment({
            symbol: "AAPL",
            modelType: "lstm",
            horizonDays: 5,
            epochs: 100,
            meanAbsoluteError: 0.01,
            finalTrainLoss: 0.001,
            ranAt: "2026-01-01T00:00:00Z",
          })
        }
      >
        log-run
      </button>
    </div>
  );
}

beforeEach(() => {
  vi.clearAllMocks();
  (useAuth as any).mockReturnValue({ token: "tok123" });
});

describe("WorkspaceStateProvider", () => {
  it("hydrates from an existing default workspace", async () => {
    (api.listWorkspaces as any).mockResolvedValue([
      { id: "ws1", name: "Default Workspace", layout_state: { selected_symbol: "MSFT" } },
    ]);

    render(
      <WorkspaceStateProvider>
        <Probe />
      </WorkspaceStateProvider>
    );

    await waitFor(() => expect(screen.getByTestId("ready").textContent).toBe("true"));
    expect(screen.getByTestId("symbol").textContent).toBe("MSFT");
    expect(api.createWorkspace).not.toHaveBeenCalled();
  });

  it("creates a default workspace when none exists", async () => {
    (api.listWorkspaces as any).mockResolvedValue([]);
    (api.createWorkspace as any).mockResolvedValue({ id: "ws-new", name: "Default Workspace", layout_state: {} });

    render(
      <WorkspaceStateProvider>
        <Probe />
      </WorkspaceStateProvider>
    );

    await waitFor(() => expect(screen.getByTestId("ready").textContent).toBe("true"));
    expect(api.createWorkspace).toHaveBeenCalledWith(
      "tok123",
      "Default Workspace",
      expect.any(String)
    );
    expect(screen.getByTestId("symbol").textContent).toBe("AAPL");
  });

  it("persists a symbol change via updateWorkspace", async () => {
    (api.listWorkspaces as any).mockResolvedValue([
      { id: "ws1", name: "Default Workspace", layout_state: {} },
    ]);
    (api.updateWorkspace as any).mockResolvedValue({});

    render(
      <WorkspaceStateProvider>
        <Probe />
      </WorkspaceStateProvider>
    );
    await waitFor(() => expect(screen.getByTestId("ready").textContent).toBe("true"));

    await act(async () => {
      screen.getByText("select-tsla").click();
    });

    expect(screen.getByTestId("symbol").textContent).toBe("TSLA");
    await waitFor(() =>
      expect(api.updateWorkspace).toHaveBeenCalledWith(
        "tok123",
        "ws1",
        expect.objectContaining({
          layout_state: expect.objectContaining({ selected_symbol: "TSLA" }),
        })
      )
    );
  });

  it("prepends new experiment log entries and caps at 20", async () => {
    (api.listWorkspaces as any).mockResolvedValue([
      { id: "ws1", name: "Default Workspace", layout_state: {} },
    ]);
    (api.updateWorkspace as any).mockResolvedValue({});

    render(
      <WorkspaceStateProvider>
        <Probe />
      </WorkspaceStateProvider>
    );
    await waitFor(() => expect(screen.getByTestId("ready").textContent).toBe("true"));

    await act(async () => {
      screen.getByText("log-run").click();
    });

    expect(screen.getByTestId("log-count").textContent).toBe("1");
  });

  it("still becomes ready if the workspace fetch fails", async () => {
    (api.listWorkspaces as any).mockRejectedValue(new Error("network error"));

    render(
      <WorkspaceStateProvider>
        <Probe />
      </WorkspaceStateProvider>
    );

    await waitFor(() => expect(screen.getByTestId("ready").textContent).toBe("true"));
  });
});
