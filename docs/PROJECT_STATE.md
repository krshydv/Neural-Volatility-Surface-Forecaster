# Hermes Forecast — Project State Checkpoint

Last updated: Session 7 (LSTM forecasting model, Redis-backed rate limiting, Prometheus/Grafana, Celery training-job queue, Google OAuth, Kubernetes manifests, frontend test scaffolding — written but largely unexecuted this session, see below)

## Branding

Product name is **HERMES FORECAST** (superseded "Volaris" as the working name this session). All user-facing text updated: landing page, sidebar, auth screens, page title, README, CLAUDE.md. Internal infra identifiers (repo folder `volaris/`, Postgres db/user `volaris`, `TOKEN_KEY` constant, test fixture emails) intentionally left as-is — not user-visible, and changing them would touch migration history for no visible benefit. See CLAUDE.md "Branding" section for the full list.

## Completed

**Phase 1 — Foundation**
- Monorepo scaffold, Postgres 16 + Redis 7 running natively, `volaris` database with `users`/`workspaces`/`assets` tables via Alembic
- FastAPI backend: full auth (register/login/refresh/me with real JWT + bcrypt), workspace CRUD with ownership isolation
- Next.js frontend: landing page, login/register pages, authenticated dashboard shell with sidebar nav matching the spec's information architecture, now rebranded to Hermes Forecast
- Design system: dark theme (ink/panel/amber-accent tokens), custom `PulseMark` waveform logo/loading motif, IBM Plex-intended typography (currently system-font fallback — see Known Issues)
- End-to-end verification via actual Playwright browser automation: registered a user through the real UI, created a workspace, reloaded the page, confirmed persistence directly against Postgres with `psql`
- Frontend: `next build`, `tsc --noEmit`, `eslint` all clean, zero errors/warnings — reverified after the rebrand
- `docker-compose.yml` and Dockerfiles for both apps written — NOT verified, this sandbox has no Docker daemon
- 11 backend tests for auth + workspaces, all passing

**Phase 3 — Quant Engine**
- `app/quant/black_scholes.py`, `greeks.py`, `implied_volatility.py`, `historical_volatility.py`, `interpolation.py`, `volatility_surface.py` — pure-function quant math, no framework dependencies
- 49 quant engine unit tests, all passing (put-call parity, arbitrage bound rejection, edge cases at zero time-to-expiry, all three interpolation methods, IV round-tripped to 1e-4 precision)
- Wired to the API: `POST /api/v1/quant/price`, `/quant/implied-volatility`, `/quant/historical-volatility` — all Bearer-auth protected, 5 API-level tests, all verified live over real HTTP

**Phase 4 — Market Data Provider (new this session)**
- `app/market_data/provider.py`: abstract `MarketDataProvider` base class (`get_assets`, `get_asset`, `get_historical_prices`, `get_options_chain`, `get_option_contract`, `get_market_events`) — matches the spec's required interface exactly
- `app/market_data/mock_provider.py`: `MockMarketDataProvider`, fully deterministic (seeded by `hash(symbol)`, not wall-clock random) — same symbol always returns the same synthetic historical prices and options chain across calls, which was verified by a dedicated test. Registry of 5 seed assets (AAPL, NVDA, SPY, TSLA, QQQ). Options chain contracts are priced through the *real* `black_scholes.price()` function using a synthetic vol-smile function (skew + term effect), not random numbers — so premiums, bid/ask spreads, and IVs are internally consistent.
- `app/market_data/factory.py`: `get_market_data_provider()` reads `MARKET_DATA_PROVIDER` from settings and returns the mock provider; raises a clear `UnsupportedProviderError` for anything else, so adding Polygon/Alpha Vantage later means writing one new adapter class and one line in this factory — no other code changes
- `app/models/asset.py`: `Asset` SQLAlchemy model, registered in `app/models/__init__.py`, migration `0d15315bedb3_create_assets_table` generated and applied (currently unused by any route — the mock provider serves assets from an in-memory registry, not the DB table; see Architecture Decisions)
- 16 provider unit tests (determinism, case-insensitive symbol lookup, unknown-symbol errors, positive-price invariants, bid≤ask invariant)
- **Wired to the API**: `GET /api/v1/assets`, `GET /api/v1/assets/{symbol}`, `GET /api/v1/assets/{symbol}/events`, `GET /api/v1/options/{symbol}/chain`, `POST /api/v1/volatility/{symbol}/surface` — the last one is the full pipeline the spec asked for: real (mock) options chain → real Black-Scholes-derived per-contract IVs → real `build_surface()` interpolation, all through one authenticated HTTP call
- 10 additional API-level tests, all passing
- Verified live over real HTTP: fetched the asset registry, pulled a 126-contract AAPL options chain, and built an 8x8 interpolated volatility surface from SPY's real chain data — all through curl against the running server

**Phase 6 — Forecasting Engine MVP (new this session)**

Scoped down deliberately from the full spec (LSTM/Transformer, training jobs, experiment tracking dashboard) to something that is genuinely real and finishable in one session, rather than scaffolding that only looks complete. What's built is a real, from-scratch, trained-live neural network — not a stub and not a hardcoded response:

- `app/forecasting/neural_net.py`: a from-scratch NumPy MLP (one hidden layer, ReLU, manual forward/backward pass, full-batch gradient descent) — no PyTorch/TensorFlow dependency, so it trains in well under a second per request
- `app/forecasting/features.py`: builds a supervised dataset from the market data provider's historical prices — rolling 5-day realized volatility, windowed into 6-step lookback sequences, standardized
- `app/forecasting/forecast_service.py`: trains the MLP live per request on a symbol's history, then forecasts forward N business days autoregressively (each step's prediction feeds the next window), with confidence bands that widen with horizon using training MAE
- Wired to `POST /api/v1/forecast/{symbol}/volatility`, Bearer-auth protected
- 15 new tests: neural net convergence on a known linear relationship, feature dataset shape/standardization invariants, forecast service behavior (positive volatility, bounds ordering, band widening, determinism for a fixed seed, unknown-symbol handling), and 4 API-level tests
- Verified live over real HTTP against a running server

**What Phase 6 explicitly is NOT**: there's no training-job queue, no experiment tracking/versioning, no LSTM/Transformer architecture, no model persistence to disk or a model registry, no walk-forward backtesting harness, no GPU path. The full spec's forecasting engine is a multi-week project on its own; this is a working, honest MVP that proves the pipeline end-to-end (provider → features → training → forecast → API → UI) so a real deep learning model can be swapped in behind the same `forecast_service.run_volatility_forecast` interface later without touching the API or frontend.

**Frontend — Options Chain, Volatility Surface, Forecast Lab, Command Palette (new this session)**

- `app/(app)/markets/assets/page.tsx`: asset list, click-through sets the shared selected symbol
- `app/(app)/markets/options-chain/page.tsx`: full calls/puts table for the selected symbol, expiry filter, consuming `GET /options/{symbol}/chain`
- `app/(app)/markets/volatility-surface/page.tsx`: renders `POST /volatility/{symbol}/surface` as a custom SVG heatmap (`components/vol-surface-heatmap.tsx`) plus smile and ATM term-structure line charts (`components/line-chart.tsx`) — both built from scratch in SVG rather than pulling in a charting dependency, so there's no new runtime dependency risk
- `app/(app)/research/forecast-lab/page.tsx`: renders the Phase 6 forecast — a forecast+band chart, model diagnostic stat cards, and a per-day detail table
- `components/command-palette.tsx`: ⌘K / Ctrl+K palette, fuzzy-filters static pages and live asset list, jumps and sets the selected symbol
- `components/asset-switcher.tsx` + `components/top-bar.tsx`: header asset switcher now present across all authenticated pages
- `lib/workspace-state-context.tsx`: `WorkspaceStateProvider` — on login, finds or auto-creates a "Default Workspace", hydrates `selectedSymbol` and volatility-surface settings from its `layout_state`, and persists on every change. This is the "continue where you left off" mechanism the plan called for; verified over live HTTP (created a workspace, patched `layout_state`, confirmed it round-trips)
- Full verification: `tsc --noEmit`, `eslint`, and `next build` all clean with zero errors after these additions. Four pre-existing `set-state-in-effect` false-positive suppressions were added, consistent with the pattern already documented for the dashboard page and auth context.

**Overall (through Session 5)**: 106/106 backend tests passing.

**Phase 7 — Analytics module: regime detection, scenario lab, risk exposure (new this session)**

- `app/analytics/regime_detection.py`: from-scratch 1D k-means (no sklearn) clustering rolling 5-day realized volatility into 3 regimes, ranked and labeled Low/Medium/High by centroid value — not fixed thresholds, so it adapts to each symbol's own volatility history
- `app/analytics/scenario.py`: shocks spot and implied volatility on a symbol's live options chain and reprices every contract through the existing real Black-Scholes + Greeks functions — no new pricing logic, just controlled inputs to code already tested in Phase 3
- `app/analytics/risk_exposure.py`: aggregates net delta/gamma/vega/theta and open-interest-weighted delta across a full chain
- Wired to `GET /api/v1/analytics/{symbol}/regime`, `POST /api/v1/analytics/{symbol}/scenario`, `GET /api/v1/analytics/{symbol}/risk`, all Bearer-auth protected
- Added `GET /api/v1/assets/{symbol}/prices` (was missing — the provider could return history but no route exposed it)
- `app/core/rate_limit.py`: real in-memory sliding-window rate limiter (120 req/60s per client IP), wired into `main.py` as middleware — honestly scoped: per-process only, would need Redis-backed counters to work correctly behind multiple replicas
- 17 new tests (3 regime, 4 scenario, 2 risk, 5 analytics API, 3 rate limiter), all passing
- Verified live over real HTTP: regime classification, chain repricing under a +10% spot / +20% vol shock, and risk aggregation all confirmed against a running server with real auth tokens

**Frontend — matching analytics/research pages (new this session)**

- `app/(app)/analytics/greeks/page.tsx`: interactive Black-Scholes + Greeks calculator, calls `/quant/price` directly
- `app/(app)/analytics/historical-volatility/page.tsx`: fetches real price history via the new `/assets/{symbol}/prices` route, charts it, and computes realized vol via `/quant/historical-volatility`
- `app/(app)/analytics/risk/page.tsx`: renders the risk exposure endpoint as stat cards
- `app/(app)/research/regime-detection/page.tsx`: current-regime badge + a colored volatility timeline bar chart (custom SVG, no new dependency) + centroid table
- `app/(app)/research/scenarios/page.tsx`: spot/vol shock sliders driving live chain repricing, shown as a sortable-by-eye table with per-contract price change
- `app/(app)/research/experiments/page.tsx`: a real (not fake) experiment log — every Forecast Lab run now appends `{symbol, horizon, epochs, MAE, train loss, timestamp}` to the workspace's `layout_state.experiment_log` via `useWorkspaceState().appendExperiment`, capped at 20 entries, and this page lists it. This is intentionally lightweight — see Known Issues for what it is not.
- `lib/api.ts` extended with typed methods for all of the above
- Full verification: `tsc --noEmit`, `eslint`, `next build` all clean, zero errors, all 14 routes build

**Overall**: 123/123 backend tests passing.

## Session 7 — LSTM, Redis rate limiting, Prometheus/Grafana, Celery jobs, Google OAuth, K8s manifests, frontend tests

**Environment change from prior sessions**: this sandbox had no network access and none of `fastapi`, `sqlalchemy`, `alembic`, `redis`, `httpx`, `celery`, `prometheus-client`, Postgres, or Redis installed, and `apps/web/node_modules` did not exist. This is a materially different (more constrained) environment than Sessions 1–6, which had all of that available. Nothing in this section carries the "verified live over real HTTP" confidence that Sessions 1–6 established — see exactly what was and wasn't executed below.

- **LSTM forecasting model** (`app/forecasting/lstm.py`): from-scratch NumPy LSTM (single layer, manual forward/backward pass, full BPTT), replacing the MLP as the new default (`model_type` request field, default `"lstm"`, `"mlp"` kept selectable for comparison). Wired through `forecast_service.py`, the Pydantic schema, the route, and the Forecast Lab frontend page (model selector + stat card); the Model Experiments log now records which model ran. **This is the one piece of new work actually executed this session**: ran standalone with real NumPy — training loss decreases over epochs, predictions have the right shape, same-seed runs are bit-identical, single-row prediction works, and the full `run_volatility_forecast` pipeline (features → model → autoregressive forecast → error handling for an unknown model type) was run end-to-end against a fake in-memory provider with real assertions, not just written and assumed correct.
- **Redis-backed rate limiting** (`app/core/rate_limit.py`): `RedisRateLimiter` using a sliding-window sorted set, `build_rate_limiter_middleware()` pings Redis at startup and falls back to the original `InMemoryRateLimiter` if unreachable — so a misconfigured or down Redis degrades to per-process limiting rather than failing closed or open. `main.py` now selects the backend via `RATE_LIMIT_BACKEND` setting. Not executed — no `redis` or `starlette` installed this session.
- **Prometheus metrics**: `app/core/metrics.py` (request counter + latency histogram) and a `/metrics` endpoint wired via middleware in `main.py`. `infrastructure/prometheus/prometheus.yml` scrape config and `infrastructure/grafana/provisioning/` (datasource + a starter dashboard JSON: req/s, p95 latency, 429 rate) added. `docker-compose.yml` gained `prometheus` and `grafana` services. Not executed.
- **Celery training-job queue**: `app/workers/celery_app.py` + `forecast_tasks.py` wrap `run_volatility_forecast` as a task; new `POST /forecast/{symbol}/volatility/jobs` (enqueue, returns 503 if the broker is unreachable rather than hanging) and `GET /forecast/jobs/{job_id}` (poll status/result). `docker-compose.yml` gained a `worker` service running `celery ... worker`. Tests written with monkeypatching so they don't require a live broker, but not executed this session (no `fastapi`/`celery` installed).
- **Google OAuth**: `app/services/oauth_service.py` (`GoogleOAuthService`, plain `httpx` calls to Google's token/userinfo endpoints, no new heavy dependency), `AuthService.login_or_register_oauth_user` (find-or-create by email, unusable random password hash for OAuth-only accounts — no schema change needed since `hashed_password` stays non-nullable), `GET /auth/oauth/google/login` + `POST /auth/oauth/google/callback` routes, and a frontend "Continue with Google" button + `/auth/callback/google` page. Requires real `GOOGLE_OAUTH_CLIENT_ID`/`SECRET` to do anything beyond a 503; tests mock `httpx.post`/`httpx.get` so they don't hit the real network. Not executed this session.
- **Kubernetes manifests** (`infrastructure/kubernetes/`): namespace, Postgres StatefulSet, Redis Deployment, API Deployment (2 replicas, migration initContainer, readiness/liveness probes against `/api/v1/ready` and `/api/v1/health`, `RATE_LIMIT_BACKEND=redis` since it's multi-replica), Celery worker Deployment, web Deployment, nginx Ingress. Never applied to a real cluster — see `infrastructure/kubernetes/README.md` for what to fix before that (image registry, real secrets management, no HPA/NetworkPolicy yet).
- **Frontend tests**: added `vitest` + `@testing-library/react` to `package.json` devDependencies (not installed — no `npm install` has happened in any sandbox session), `vitest.config.ts`/`vitest.setup.ts`, and three test files: `pulse-mark.test.tsx`, `line-chart.test.tsx` (checked against the actual component source — it renders one `<polyline>` per series, viewBox `0 0 560 260`), and `auth-context.test.tsx` (mocks the `api` module, exercises login/logout/localStorage persistence). None of these have been run.

**What Session 7 explicitly did not attempt**: verifying Docker Compose or the K8s manifests against real Docker/Kubernetes (no daemon/cluster available, same as every prior session); running the frontend toolchain at all; running the backend test suite (no `pytest`/`fastapi` installed, so the 123 previously-passing tests plus the new ones written this session — LSTM, forecast model-type, rate-limit fallback, metrics, forecast jobs, OAuth — have not been re-run as a whole; only the pure-NumPy forecasting path was actually executed, as described above).

## Session 8 — additional frontend test coverage, K8s hardening (HPA/PDB/NetworkPolicy)

Same environment constraints as Session 7 (no network, no `fastapi`/`node_modules`/Postgres/Redis/Docker/K8s). Two more genuinely-complete-able-by-writing-code items from the Session 7 "remaining work" list were finished:

- **Frontend test coverage extended**: added `workspace-state-context.test.tsx` (hydration from an existing workspace, auto-creating a default workspace when none exists, persisting a symbol change via `updateWorkspace`, appending to the experiment log, and staying `ready` even if the initial fetch fails) alongside the Session 7 `auth-context`/`pulse-mark`/`line-chart` tests. All mock the `api` module and `useAuth`, so they don't need a live backend — but like all frontend tests so far, they've never actually been run through `vitest` (no `npm install` has happened in any sandbox session). Page-level tests for the analytics/research pages were deliberately not attempted: those pages make several distinct API calls each and would need substantial mocking to test meaningfully, and no lib-level pure functions exist to unit-test in isolation (all computation is server-side) — extending page coverage is still open.
- **Kubernetes hardening**: `infrastructure/kubernetes/autoscaling.yaml` (HPA for `api` and `worker` on CPU utilization, PodDisruptionBudgets for `api` and `web`) and `network-policy.yaml` (default-deny ingress + explicit allow rules: web→api, api/worker→postgres, api/worker→redis, ingress-controller→web). All new K8s YAML was parsed with `yaml.safe_load_all` to confirm it's syntactically valid — that's the extent of what could be checked without a real cluster. `README.md` updated with apply order and the caveat that `NetworkPolicy` only does anything if the cluster's CNI enforces it.
- Also re-validated every YAML/JSON file added in Sessions 7–8 (`docker-compose.yml`, all of `infrastructure/`) by actually parsing them with Python's `yaml`/`json` modules — all parse cleanly. New `.tsx` test files were only checked for brace-balance via a quick Node script, which is a very weak substitute for a real TypeScript/JSX parse; treat them as unverified until `vitest` actually runs them.

**What's left that genuinely cannot be completed by writing more code in this sandbox**, no matter how many further turns: everything in the Session 7 "Next Steps" list (1–5) requires a real Docker daemon, a real Kubernetes cluster, real Google OAuth credentials, or `npm`/`pip` with network access to install dependencies — none of which have been available in any session so far. The honest scope of "finished" here is: all planned code exists, is internally consistent, and has been checked as thoroughly as static analysis and pure-Python/NumPy execution allow; none of it has been proven correct by actually running the full stack.

1. In a real environment: `pip install -r requirements.txt` (or venv) and `npm install`, then re-run the full backend `pytest` suite and `npx vitest run` / `next build` — Session 7's backend/frontend additions are unexecuted code until this happens.
2. Verify `docker compose up --build` end-to-end in a real Docker environment, including the new `worker`, `prometheus`, and `grafana` services.
3. Apply the Kubernetes manifests to a real cluster (kind/minikube is enough to start) and fix whatever the first real apply surfaces — image names/registry are placeholders.
4. Register real Google OAuth credentials and click through the login flow in an actual browser.
5. Point a load test at the API with `RATE_LIMIT_BACKEND=redis` and confirm the sliding-window limiter behaves correctly under concurrent replicas — this was reasoned through but never run against real Redis.
6. Frontend test coverage is a start (3 files) — extend to the analytics/research pages and the workspace-state persistence logic next.

## Known Issues

- Docker Compose files exist but have never actually been run — no Docker daemon available in this development sandbox. Verify `docker compose up --build` in a real Docker environment before relying on it.
- Postgres and Redis do not persist as running processes between sandbox sessions/idles (though the Postgres data directory persists on disk) — this bit us twice this session. Every new session/after any idle period, run `service postgresql start` and `redis-server --daemonize yes` before touching the API.
- `uvicorn`/`next dev` background processes also don't survive a sandbox idle/reset and need `setsid ... &` to survive tool-call boundaries; `--reload` was observed to die shortly after starting even under setsid, so uvicorn runs without it and is restarted manually after route changes.
- Google Fonts (`fonts.googleapis.com`) is not in this sandbox's network allowlist, so the frontend uses system font fallback instead of the intended IBM Plex Sans/Mono pairing.
- No rate limiting, no OAuth, no Celery task wiring, no Prometheus/Grafana — all architecturally anticipated, none implemented.
- No frontend tests exist yet (component tests, flow tests) — only backend has automated tests.
- `Asset` DB model exists and is migrated but is currently dead weight — the mock provider doesn't read from or write to it. Decide before Phase 2 "real provider" work whether assets should be DB-backed (for user-added custom tickers) or provider-sourced only.

## Architecture Decisions

- **System Python over venv**: `source` is unavailable in the sandbox's `sh`-based tool runtime, so backend dependencies are installed into system Python with `pip install --break-system-packages`. A real dev environment should use a proper venv (`requirements.txt` is venv-compatible as-is).
- **Repository/Service split**: repositories only do data access, services own business rules and ownership checks, routes only translate between HTTP and services. Applied to auth and workspaces; market data uses a simpler provider-injection pattern instead since it's read-only external data, not owned application state.
- **JSON `layout_state` column on Workspace**: chosen over a normalized layout schema so the frontend can persist arbitrary UI state without backend schema churn.
- **Quant engine as pure functions**: no FastAPI or SQLAlchemy imports anywhere in `app/quant/`, reusable from API routes, Celery workers, or a future standalone `services/quant-engine` process without rewriting.
- **IV solver tries Newton-Raphson before Brent**: Newton converges fast for well-behaved options; Brent (bisection) is the guaranteed-convergent fallback for harder cases like deep OTM where vega is small.
- **Market data provider is fully decoupled from the database**: `MarketDataProvider` is an abstract interface injected via FastAPI `Depends`, matching the spec's explicit requirement not to hardcode provider logic throughout the app. The mock implementation is deterministic (seeded, not time-based random) specifically so tests and demos are reproducible.
- **Mock options chain premiums are computed, not faked**: contract prices come from the real `black_scholes.price()` function fed a synthetic-but-structured (skewed, term-sloped) volatility surface, not arbitrary random numbers. This means the mock data has internally consistent no-arbitrage relationships, which matters because the volatility surface endpoint round-trips this same data back through the IV/surface math.
- **No comments in code**: per explicit user preference, all code across this project omits comments and docstrings.

## Session 9 — merged the real blue/white redesign

The `hermes-forecast-redesign.zip` uploaded this session was genuinely different from the base archive — an earlier development snapshot (predates the Session 6-8 backend work: no LSTM/OAuth/analytics/rate-limiter) with a real, complete redesign applied to the frontend: electric blue (`#0b08f5`) + white palette, editorial serif (`Fraunces`, with system-font fallback for the same no-network reason IBM Plex had) + mono (`DM Mono`) typography, "NOUS Portal"-inspired sidebar chrome and "Hermes Agent"-inspired editorial landing page. This is a different file from the byte-identical one flagged in Session 6 — that earlier upload was apparently an export mistake, not evidence the redesign never existed.

**How it was merged** (backend was untouched — this was frontend-only):
- `app/globals.css` replaced wholesale with the redesign's token system (`--color-primary`, `--color-background`, `--color-surface`, `--color-text-*`, `--color-border`, etc.), **plus backward-compatible aliases** (`--color-ink: var(--color-background)`, `--color-panel: var(--color-surface)`, `--color-accent-amber: var(--color-primary)`, etc.) mapping every old dark/amber token name to its new equivalent. This means the 14 pages built after the original redesign export (all of `analytics/`, `markets/`, `research/`, dashboard, asset-switcher, command-palette) pick up the new blue/white look automatically, without being individually rewritten — they were never touched this session and still reference the old class names, which now resolve to the new palette via the alias.
- Hand-merged (not just copied) into the new design: `app/layout.tsx`, `app/page.tsx` (landing), `app/(auth)/layout.tsx`, `app/(auth)/register/page.tsx`, `components/sidebar.tsx`, `components/pulse-mark.tsx` — copied from the redesign zip largely as-is, since they predate and don't conflict with later features.
- `app/(auth)/login/page.tsx` was a **real merge**, not a copy: the redesign zip's login page predates the Session 8 Google OAuth work, so it was rebuilt using the redesign's visual markup with the "Continue with Google" button and its handler logic reinserted.
- `app/(app)/layout.tsx` and `components/top-bar.tsx` were adapted (new background token, new `label-tag`/border styling) rather than replaced outright, since they wire in `WorkspaceStateProvider`, `CommandPalette`, and `TopBar`/`AssetSwitcher` — none of which existed in the redesign snapshot.
- Verified the new `pulse-mark.tsx` still satisfies the existing `pulse-mark.test.tsx` assertions (viewBox, animate-class toggling, className forwarding) by reading both side by side — all four assertions still hold structurally.
- Grepped every `.tsx` file in `app/` and `components/` for any color utility class not covered by either the new or the aliased-old token set — none found; the 14 auto-restyled pages only use token names that resolve correctly.

**Not verified this session** (same constraint as always — no network/npm in this sandbox): none of this has actually been rendered by `next dev`/`next build`. The alias strategy is sound in principle (Tailwind v4 `@theme inline` generates utilities from whatever CSS custom properties are registered, regardless of how many indirection hops the `var()` chain has), but the first real build is still the first time this gets proven, not assumed.
