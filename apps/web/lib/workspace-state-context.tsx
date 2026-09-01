"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

interface SurfaceSettings {
  method: string;
  gridResolution: number;
}

interface WorkspaceStateValue {
  ready: boolean;
  selectedSymbol: string;
  setSelectedSymbol: (symbol: string) => void;
  surfaceSettings: SurfaceSettings;
  setSurfaceSettings: (settings: SurfaceSettings) => void;
  experimentLog: ExperimentLogEntry[];
  appendExperiment: (entry: ExperimentLogEntry) => void;
}

export interface ExperimentLogEntry {
  symbol: string;
  modelType: string;
  horizonDays: number;
  epochs: number;
  meanAbsoluteError: number;
  finalTrainLoss: number;
  ranAt: string;
}

const DEFAULT_SYMBOL = "AAPL";
const DEFAULT_SURFACE: SurfaceSettings = { method: "linear", gridResolution: 12 };
const PRIMARY_WORKSPACE_NAME = "Default Workspace";

const WorkspaceStateContext = createContext<WorkspaceStateValue | undefined>(undefined);

export function WorkspaceStateProvider({ children }: { children: React.ReactNode }) {
  const { token } = useAuth();
  const [ready, setReady] = useState(false);
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [selectedSymbol, setSelectedSymbolState] = useState(DEFAULT_SYMBOL);
  const [surfaceSettings, setSurfaceSettingsState] = useState<SurfaceSettings>(DEFAULT_SURFACE);
  const [experimentLog, setExperimentLog] = useState<ExperimentLogEntry[]>([]);
  const hydrated = useRef(false);

  useEffect(() => {
    if (!token || hydrated.current) return;
    hydrated.current = true;

    (async () => {
      const workspaces = await api.listWorkspaces(token);
      let primary = workspaces.find((w) => w.name === PRIMARY_WORKSPACE_NAME) ?? workspaces[0];

      if (!primary) {
        primary = await api.createWorkspace(token, PRIMARY_WORKSPACE_NAME, "Auto-created to persist market view state");
      }

      setWorkspaceId(primary.id);
      const layout = primary.layout_state ?? {};
      if (typeof layout.selected_symbol === "string") {
        setSelectedSymbolState(layout.selected_symbol);
      }
      if (layout.surface_settings && typeof layout.surface_settings === "object") {
        const stored = layout.surface_settings as Partial<SurfaceSettings>;
        setSurfaceSettingsState({
          method: stored.method ?? DEFAULT_SURFACE.method,
          gridResolution: stored.gridResolution ?? DEFAULT_SURFACE.gridResolution,
        });
      }
      if (Array.isArray(layout.experiment_log)) {
        setExperimentLog(layout.experiment_log as ExperimentLogEntry[]);
      }
      setReady(true);
    })().catch(() => setReady(true));
  }, [token]);

  const persist = useCallback(
    (patch: Record<string, unknown>) => {
      if (!token || !workspaceId) return;
      api
        .updateWorkspace(token, workspaceId, {
          layout_state: {
            selected_symbol: selectedSymbol,
            surface_settings: surfaceSettings,
            experiment_log: experimentLog,
            ...patch,
          },
        })
        .catch(() => undefined);
    },
    [token, workspaceId, selectedSymbol, surfaceSettings, experimentLog]
  );

  const setSelectedSymbol = useCallback(
    (symbol: string) => {
      setSelectedSymbolState(symbol);
      persist({ selected_symbol: symbol });
    },
    [persist]
  );

  const setSurfaceSettings = useCallback(
    (settings: SurfaceSettings) => {
      setSurfaceSettingsState(settings);
      persist({ surface_settings: settings });
    },
    [persist]
  );

  const appendExperiment = useCallback(
    (entry: ExperimentLogEntry) => {
      setExperimentLog((prev) => {
        const next = [entry, ...prev].slice(0, 20);
        persist({ experiment_log: next });
        return next;
      });
    },
    [persist]
  );

  return (
    <WorkspaceStateContext.Provider
      value={{
        ready,
        selectedSymbol,
        setSelectedSymbol,
        surfaceSettings,
        setSurfaceSettings,
        experimentLog,
        appendExperiment,
      }}
    >
      {children}
    </WorkspaceStateContext.Provider>
  );
}

export function useWorkspaceState() {
  const context = useContext(WorkspaceStateContext);
  if (!context) {
    throw new Error("useWorkspaceState must be used within WorkspaceStateProvider");
  }
  return context;
}
