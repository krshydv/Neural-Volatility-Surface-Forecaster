const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string> | undefined),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });

  if (response.status === 204) {
    return undefined as T;
  }

  const body = await response.json().catch(() => ({}));

  if (!response.ok) {
    const message = typeof body.detail === "string" ? body.detail : "Request failed";
    throw new ApiError(response.status, message);
  }

  return body as T;
}

export interface UserRead {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface WorkspaceRead {
  id: string;
  name: string;
  description: string | null;
  layout_state: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AssetRead {
  symbol: string;
  name: string;
  asset_class: string;
  last_price: number;
}

export interface OptionContractRead {
  symbol: string;
  strike: number;
  expiry: string;
  option_type: "call" | "put";
  bid: number;
  ask: number;
  last: number;
  implied_volatility: number;
  open_interest: number;
  volume: number;
}

export interface OptionsChainRead {
  symbol: string;
  spot: number;
  as_of: string;
  contracts: OptionContractRead[];
}

export interface VolatilitySurfaceRead {
  symbol: string;
  spot: number;
  method: string;
  moneyness_grid: number[];
  expiry_grid: number[];
  volatility_grid: number[][];
}

export interface ForecastPointRead {
  forecast_date: string;
  volatility: number;
  lower_bound: number;
  upper_bound: number;
}

export type ForecastModelType = "mlp" | "lstm";

export interface VolatilityForecastRead {
  symbol: string;
  model_type: ForecastModelType;
  horizon_days: number;
  trained_on_observations: number;
  epochs: number;
  final_train_loss: number;
  mean_absolute_error: number;
  points: ForecastPointRead[];
}

export interface PricePointRead {
  trade_date: string;
  close: number;
}

export interface RegimePointRead {
  trade_date: string;
  realized_vol: number;
  regime_index: number;
  regime_label: string;
}

export interface RegimeDetectionRead {
  symbol: string;
  points: RegimePointRead[];
  centroids: number[];
  current_regime: string;
}

export interface ScenarioContractRead {
  symbol: string;
  strike: number;
  expiry: string;
  option_type: "call" | "put";
  base_price: number;
  shocked_price: number;
  price_change_pct: number;
  base_delta: number;
  shocked_delta: number;
}

export interface ScenarioResultRead {
  symbol: string;
  base_spot: number;
  shocked_spot: number;
  spot_shock_pct: number;
  vol_shock_pct: number;
  total_delta_change_pct: number;
  contracts: ScenarioContractRead[];
}

export interface RiskExposureRead {
  symbol: string;
  spot: number;
  contract_count: number;
  net_delta: number;
  net_gamma: number;
  net_vega: number;
  net_theta: number;
  open_interest_weighted_delta: number;
}

export interface OptionPricingResult {
  call_price: number;
  put_price: number;
  call_greeks: Record<string, number>;
  put_greeks: Record<string, number>;
}

export const api = {
  register: (email: string, password: string, fullName?: string) =>
    request<UserRead>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName ?? null }),
    }),

  login: (email: string, password: string) =>
    request<TokenPair>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: (token: string) => request<UserRead>("/auth/me", {}, token),

  getGoogleLoginUrl: () =>
    request<{ authorization_url: string; state: string }>("/auth/oauth/google/login"),

  googleCallback: (code: string) =>
    request<TokenPair>("/auth/oauth/google/callback", {
      method: "POST",
      body: JSON.stringify({ code }),
    }),

  listWorkspaces: (token: string) =>
    request<WorkspaceRead[]>("/workspaces", {}, token),

  createWorkspace: (token: string, name: string, description?: string) =>
    request<WorkspaceRead>(
      "/workspaces",
      { method: "POST", body: JSON.stringify({ name, description: description ?? null }) },
      token
    ),

  deleteWorkspace: (token: string, id: string) =>
    request<void>(`/workspaces/${id}`, { method: "DELETE" }, token),

  updateWorkspace: (
    token: string,
    id: string,
    payload: { name?: string; description?: string; layout_state?: Record<string, unknown> }
  ) =>
    request<WorkspaceRead>(
      `/workspaces/${id}`,
      { method: "PATCH", body: JSON.stringify(payload) },
      token
    ),

  listAssets: (token: string) => request<AssetRead[]>("/assets", {}, token),

  getAsset: (token: string, symbol: string) =>
    request<AssetRead>(`/assets/${symbol}`, {}, token),

  getOptionsChain: (token: string, symbol: string) =>
    request<OptionsChainRead>(`/options/${symbol}/chain`, {}, token),

  getVolatilitySurface: (
    token: string,
    symbol: string,
    method: string = "linear",
    gridResolution: number = 12
  ) =>
    request<VolatilitySurfaceRead>(
      `/volatility/${symbol}/surface`,
      {
        method: "POST",
        body: JSON.stringify({ method, grid_resolution: gridResolution }),
      },
      token
    ),

  getForecast: (
    token: string,
    symbol: string,
    horizonDays: number = 10,
    epochs: number = 400,
    modelType: ForecastModelType = "lstm"
  ) =>
    request<VolatilityForecastRead>(
      `/forecast/${symbol}/volatility`,
      {
        method: "POST",
        body: JSON.stringify({ horizon_days: horizonDays, epochs, model_type: modelType }),
      },
      token
    ),

  getAssetPrices: (token: string, symbol: string, days: number = 180) =>
    request<PricePointRead[]>(`/assets/${symbol}/prices?days=${days}`, {}, token),

  getRegimeDetection: (token: string, symbol: string) =>
    request<RegimeDetectionRead>(`/analytics/${symbol}/regime`, {}, token),

  runScenario: (token: string, symbol: string, spotShockPct: number, volShockPct: number) =>
    request<ScenarioResultRead>(
      `/analytics/${symbol}/scenario`,
      {
        method: "POST",
        body: JSON.stringify({ spot_shock_pct: spotShockPct, vol_shock_pct: volShockPct }),
      },
      token
    ),

  getRiskExposure: (token: string, symbol: string) =>
    request<RiskExposureRead>(`/analytics/${symbol}/risk`, {}, token),

  priceOption: (
    token: string,
    payload: {
      spot: number;
      strike: number;
      time_to_expiry: number;
      risk_free_rate: number;
      volatility: number;
      dividend_yield?: number;
    }
  ) =>
    request<OptionPricingResult>(
      `/quant/price`,
      { method: "POST", body: JSON.stringify(payload) },
      token
    ),

  getHistoricalVolatility: (token: string, prices: number[], tradingDaysPerYear: number = 252) =>
    request<{ realized_volatility: number }>(
      `/quant/historical-volatility`,
      {
        method: "POST",
        body: JSON.stringify({ prices, trading_days_per_year: tradingDaysPerYear }),
      },
      token
    ),
};
