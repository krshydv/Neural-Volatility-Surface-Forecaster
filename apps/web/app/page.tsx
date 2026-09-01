import Link from "next/link";
import { PulseMark } from "@/components/pulse-mark";

export default function LandingPage() {
  return (
    <main className="flex min-h-screen flex-col bg-background">
      {/* Full-bleed blue nav + hero, matching the Hermes Agent reference */}
      <div className="bg-primary">
        <header className="flex items-center justify-between px-6 sm:px-10 py-6 max-w-[1400px] mx-auto">
          <Link href="/" className="flex items-center gap-3">
            <PulseMark className="h-5 w-16" inverse />
            <span className="label-tag text-text-inverse">Hermes Forecast</span>
          </Link>
          <nav className="flex items-center gap-6">
            <Link
              href="/login"
              className="label-tag text-text-inverse-muted hover:text-text-inverse transition-colors"
            >
              Sign in
            </Link>
            <Link
              href="/register"
              className="btn px-5 py-2.5 bg-background text-primary hover:bg-primary-soft"
            >
              Create account
            </Link>
          </nav>
        </header>

        <section className="px-6 sm:px-10 py-20 sm:py-28 max-w-[1400px] w-full mx-auto">
          <span className="label-tag text-text-inverse-muted mb-6 block">
            Open beta · Neural volatility intelligence
          </span>
          <h1
            className="font-display uppercase text-text-inverse leading-[0.92] tracking-[-0.02em] max-w-5xl"
            style={{ fontSize: "clamp(44px, 7.5vw, 110px)" }}
          >
            Read the volatility
            <br />
            surface before the
            <br />
            market does
          </h1>
          <p className="mt-8 max-w-xl text-text-inverse-muted text-sm leading-relaxed font-mono tracking-wide">
            Options analytics, neural forecasting, and regime detection in one
            research workstation built for quantitative teams.
          </p>
          <div className="mt-10 flex items-center gap-4">
            <Link
              href="/register"
              className="btn px-6 py-3.5 bg-background text-primary hover:bg-primary-soft"
            >
              Start research
            </Link>
            <Link
              href="/login"
              className="btn px-6 py-3.5 border border-text-inverse text-text-inverse hover:bg-white/10"
            >
              Sign in
            </Link>
          </div>
        </section>
      </div>

      {/* White feature section with solid blue placeholder blocks, matching
          the Hermes Agent "#1 Connect / #2 Remember / #3 Schedule" grid */}
      <section className="bg-background px-6 sm:px-10 py-20 sm:py-28">
        <div className="max-w-[1400px] mx-auto">
          <span className="label-tag text-primary mb-14 block">
            Why Hermes Forecast
          </span>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-16">
            <div>
              <span className="label-tag text-text-muted">#1 Surfaces</span>
              <h3 className="font-display uppercase text-3xl sm:text-4xl leading-[0.95] text-text-primary mt-4 mb-6">
                Volatility
                <br />
                Surfaces
              </h3>
              <div className="image-block h-56 mb-6" />
              <p className="text-text-secondary text-xs leading-relaxed font-mono tracking-wide max-w-xs">
                Construct and interpolate implied volatility surfaces from
                live options chains, with Black-Scholes and Greeks computed
                inline.
              </p>
            </div>
            <div>
              <span className="label-tag text-text-muted">#2 Forecasting</span>
              <h3 className="font-display uppercase text-3xl sm:text-4xl leading-[0.95] text-text-primary mt-4 mb-6">
                Neural
                <br />
                Forecasting
              </h3>
              <div className="image-block h-56 mb-6" />
              <p className="text-text-secondary text-xs leading-relaxed font-mono tracking-wide max-w-xs">
                Forecast forward volatility regimes using models trained on
                historical surfaces, scenario-tested before you trade on
                them.
              </p>
            </div>
            <div>
              <span className="label-tag text-text-muted">#3 Workspaces</span>
              <h3 className="font-display uppercase text-3xl sm:text-4xl leading-[0.95] text-text-primary mt-4 mb-6">
                Research
                <br />
                Workspaces
              </h3>
              <div className="image-block h-56 mb-6" />
              <p className="text-text-secondary text-xs leading-relaxed font-mono tracking-wide max-w-xs">
                Every analysis persists to a saved workspace, so your team
                picks up exactly where the research left off.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Mega wordmark section, echoing the reference's edge-to-edge display
          typography moment */}
      <section className="bg-background overflow-hidden pb-4">
        <div
          className="font-display uppercase text-primary leading-[0.75] tracking-[-0.04em] whitespace-nowrap px-4"
          style={{ fontSize: "clamp(90px, 15vw, 260px)" }}
        >
          Hermes Forecast
        </div>
      </section>

      <footer className="bg-primary px-6 sm:px-10 py-8 flex flex-col sm:flex-row items-center justify-between gap-2 label-tag text-text-inverse-muted">
        <span>Hermes Forecast</span>
        <span>Neural Volatility Intelligence</span>
        <span>Internal build</span>
      </footer>
    </main>
  );
}
