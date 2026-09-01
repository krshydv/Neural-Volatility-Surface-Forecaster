import math
import random
from datetime import date, datetime, timedelta, timezone

from app.market_data.provider import MarketDataProvider
from app.market_data.types import (
    AssetInfo,
    MarketEventInfo,
    OptionContractInfo,
    OptionsChainSnapshot,
    PricePoint,
)
from app.quant.black_scholes import BlackScholesInputs, OptionType, price

ASSET_REGISTRY: dict[str, AssetInfo] = {
    "AAPL": AssetInfo(symbol="AAPL", name="Apple Inc.", asset_class="equity", last_price=228.50),
    "MSFT": AssetInfo(symbol="MSFT", name="Microsoft Corporation", asset_class="equity", last_price=441.80),
    "GOOGL": AssetInfo(symbol="GOOGL", name="Alphabet Inc. Class A", asset_class="equity", last_price=178.35),
    "AMZN": AssetInfo(symbol="AMZN", name="Amazon.com, Inc.", asset_class="equity", last_price=205.60),
    "NVDA": AssetInfo(symbol="NVDA", name="NVIDIA Corporation", asset_class="equity", last_price=138.20),
    "META": AssetInfo(symbol="META", name="Meta Platforms, Inc.", asset_class="equity", last_price=595.40),
    "TSLA": AssetInfo(symbol="TSLA", name="Tesla, Inc.", asset_class="equity", last_price=262.75),
    "AVGO": AssetInfo(symbol="AVGO", name="Broadcom Inc.", asset_class="equity", last_price=182.90),
    "NFLX": AssetInfo(symbol="NFLX", name="Netflix, Inc.", asset_class="equity", last_price=890.15),
    "JPM": AssetInfo(symbol="JPM", name="JPMorgan Chase & Co.", asset_class="equity", last_price=241.30),
    "BAC": AssetInfo(symbol="BAC", name="Bank of America Corporation", asset_class="equity", last_price=44.75),
    "XOM": AssetInfo(symbol="XOM", name="Exxon Mobil Corporation", asset_class="equity", last_price=118.40),
    "JNJ": AssetInfo(symbol="JNJ", name="Johnson & Johnson", asset_class="equity", last_price=156.20),
    "UNH": AssetInfo(symbol="UNH", name="UnitedHealth Group Incorporated", asset_class="equity", last_price=502.10),
    "HD": AssetInfo(symbol="HD", name="The Home Depot, Inc.", asset_class="equity", last_price=398.65),
    "DIS": AssetInfo(symbol="DIS", name="The Walt Disney Company", asset_class="equity", last_price=112.85),
    "PLTR": AssetInfo(symbol="PLTR", name="Palantir Technologies Inc.", asset_class="equity", last_price=78.40),
    "COIN": AssetInfo(symbol="COIN", name="Coinbase Global, Inc.", asset_class="equity", last_price=289.60),
    "SPY": AssetInfo(symbol="SPY", name="SPDR S&P 500 ETF Trust", asset_class="etf", last_price=575.10),
    "QQQ": AssetInfo(symbol="QQQ", name="Invesco QQQ Trust", asset_class="etf", last_price=490.30),
    "IWM": AssetInfo(symbol="IWM", name="iShares Russell 2000 ETF", asset_class="etf", last_price=224.80),
    "VXX": AssetInfo(symbol="VXX", name="iPath Series B S&P 500 VIX Short-Term Futures ETN", asset_class="etf", last_price=52.15),
    "GLD": AssetInfo(symbol="GLD", name="SPDR Gold Shares", asset_class="etf", last_price=248.90),
}

EXPIRY_OFFSETS_DAYS = [7, 14, 30, 60, 90, 180, 365]
STRIKE_MONEYNESS_STEPS = [0.8, 0.85, 0.9, 0.95, 1.0, 1.05, 1.1, 1.15, 1.2]
RISK_FREE_RATE = 0.045


def _seed_for(symbol: str, salt: str = "") -> int:
    return abs(hash(f"{symbol}:{salt}")) % (2**31)


def _base_volatility(symbol: str) -> float:
    rng = random.Random(_seed_for(symbol, "base_vol"))
    return round(rng.uniform(0.18, 0.45), 4)


def _smile_volatility(base_vol: float, moneyness: float, expiry_years: float) -> float:
    skew = (1.0 - moneyness) * 0.35
    term_effect = 0.05 * math.sqrt(expiry_years)
    smile = base_vol + skew + term_effect
    return max(smile, 0.05)


class MockMarketDataProvider(MarketDataProvider):
    def get_assets(self) -> list[AssetInfo]:
        return list(ASSET_REGISTRY.values())

    def get_asset(self, symbol: str) -> AssetInfo | None:
        return ASSET_REGISTRY.get(symbol.upper())

    def get_historical_prices(
        self, symbol: str, start: date, end: date
    ) -> list[PricePoint]:
        asset = self.get_asset(symbol)
        if asset is None:
            raise ValueError(f"Unknown symbol: {symbol}")
        if start > end:
            raise ValueError("start date must not be after end date")

        rng = random.Random(_seed_for(symbol, "prices"))
        num_days = (end - start).days + 1
        daily_vol = _base_volatility(symbol) / math.sqrt(252)
        price_val = asset.last_price

        points: list[PricePoint] = []
        current = start
        for _ in range(num_days):
            drift = 0.0001
            shock = rng.gauss(drift, daily_vol)
            price_val *= math.exp(shock)
            points.append(PricePoint(trade_date=current, close=round(price_val, 4)))
            current += timedelta(days=1)

        return points

    def get_options_chain(self, symbol: str) -> OptionsChainSnapshot:
        asset = self.get_asset(symbol)
        if asset is None:
            raise ValueError(f"Unknown symbol: {symbol}")

        base_vol = _base_volatility(symbol)
        rng = random.Random(_seed_for(symbol, "chain"))
        spot = asset.last_price
        today = date.today()

        contracts: list[OptionContractInfo] = []
        for offset_days in EXPIRY_OFFSETS_DAYS:
            expiry = today + timedelta(days=offset_days)
            expiry_years = offset_days / 365.0

            for step in STRIKE_MONEYNESS_STEPS:
                strike = round(spot * step, 2)
                vol = _smile_volatility(base_vol, step, expiry_years)

                for option_type, enum_type in [("call", OptionType.CALL), ("put", OptionType.PUT)]:
                    inputs = BlackScholesInputs(
                        spot=spot,
                        strike=strike,
                        time_to_expiry=expiry_years,
                        risk_free_rate=RISK_FREE_RATE,
                        volatility=vol,
                    )
                    theo_price = price(inputs, enum_type)
                    spread = max(theo_price * 0.02, 0.01)

                    contracts.append(
                        OptionContractInfo(
                            symbol=f"{symbol}{expiry.strftime('%y%m%d')}{option_type[0].upper()}{int(strike * 1000):08d}",
                            strike=strike,
                            expiry=expiry,
                            option_type=option_type,
                            bid=round(max(theo_price - spread / 2, 0.0), 2),
                            ask=round(theo_price + spread / 2, 2),
                            last=round(theo_price, 2),
                            implied_volatility=round(vol, 4),
                            open_interest=rng.randint(0, 5000),
                            volume=rng.randint(0, 1200),
                        )
                    )

        return OptionsChainSnapshot(
            symbol=symbol,
            spot=spot,
            as_of=datetime.now(timezone.utc),
            contracts=contracts,
        )

    def get_option_contract(
        self, symbol: str, strike: float, expiry: date, option_type: str
    ) -> OptionContractInfo | None:
        chain = self.get_options_chain(symbol)
        for contract in chain.contracts:
            if (
                contract.strike == strike
                and contract.expiry == expiry
                and contract.option_type == option_type
            ):
                return contract
        return None

    def get_market_events(self, symbol: str | None = None) -> list[MarketEventInfo]:
        symbols = [symbol.upper()] if symbol else list(ASSET_REGISTRY.keys())
        events: list[MarketEventInfo] = []
        today = date.today()

        for sym in symbols:
            if sym not in ASSET_REGISTRY:
                continue
            rng = random.Random(_seed_for(sym, "events"))
            events.append(
                MarketEventInfo(
                    symbol=sym,
                    event_type="earnings",
                    title=f"{sym} Q{rng.randint(1, 4)} Earnings Call",
                    event_date=today + timedelta(days=rng.randint(3, 45)),
                )
            )
            events.append(
                MarketEventInfo(
                    symbol=sym,
                    event_type="volatility_event",
                    title=f"Implied volatility elevated for {sym}",
                    event_date=today - timedelta(days=rng.randint(0, 5)),
                )
            )
            if rng.random() < 0.6:
                rating = rng.choice(["Overweight", "Buy", "Neutral", "Hold", "Underweight"])
                bank = rng.choice(
                    ["Morgan Stanley", "Goldman Sachs", "JPMorgan", "Barclays", "Citi", "UBS"]
                )
                events.append(
                    MarketEventInfo(
                        symbol=sym,
                        event_type="analyst_rating",
                        title=f"{bank} initiates {sym} at {rating}",
                        event_date=today - timedelta(days=rng.randint(0, 10)),
                    )
                )
            if rng.random() < 0.35:
                action = rng.choice(
                    ["announces share buyback program", "declares quarterly dividend", "completes secondary offering"]
                )
                events.append(
                    MarketEventInfo(
                        symbol=sym,
                        event_type="corporate_action",
                        title=f"{sym} {action}",
                        event_date=today + timedelta(days=rng.randint(1, 30)),
                    )
                )

        return events
