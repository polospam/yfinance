import yfinance as yf
import pandas as pd
import numpy as np
from typing import Tuple


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff().astype(float)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    up_move = high - high.shift()
    down_move = low.shift() - low

    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

    atr = true_range.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
    adx = dx.rolling(window=period).mean()
    return adx, plus_di, minus_di


def calculate_stochastic(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    k_period: int = 14,
    d_period: int = 3,
) -> Tuple[pd.Series, pd.Series]:
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
    d = k.rolling(window=d_period).mean()
    return k, d


def calculate_roc(prices: pd.Series, period: int = 10) -> pd.Series:
    return ((prices - prices.shift(period)) / prices.shift(period)) * 100


def interpret_rsi(value: float) -> str:
    if value >= 70:
        return "Overbought ⚠️"
    elif value <= 30:
        return "Oversold ⚠️"
    elif value >= 55:
        return "Bullish 📈"
    elif value <= 45:
        return "Bearish 📉"
    else:
        return "Neutral ➡️"


def interpret_macd(macd: float, signal: float, histogram: float) -> str:
    if macd > signal and histogram > 0:
        return "Bullish (MACD above signal) 📈"
    elif macd < signal and histogram < 0:
        return "Bearish (MACD below signal) 📉"
    else:
        return "Crossing / Transitioning ↔️"


def interpret_adx(value: float) -> str:
    if value >= 50:
        return "Very Strong Trend 💪"
    elif value >= 25:
        return "Strong Trend ✅"
    elif value >= 20:
        return "Developing Trend 🔄"
    else:
        return "Weak / No Trend ❌"


def analyze_momentum(ticker: str, period: str = "2y") -> None:
    print(f"\n{'='*55}")
    print(f"  MOMENTUM ANALYSIS: {ticker.upper()}")
    print(f"{'='*55}")

    stock = yf.Ticker(ticker)
    df = stock.history(period=period)

    if df.empty:
        print(f"❌ No data found for ticker '{ticker}'. Check the symbol.")
        return

    close: pd.Series = df["Close"]
    high: pd.Series = df["High"]
    low: pd.Series = df["Low"]
    volume: pd.Series = df["Volume"]

    # --- Current price info ---
    current_price: float = close.iloc[-1]
    prev_price: float = close.iloc[-2]
    price_change: float = current_price - prev_price
    pct_change: float = (price_change / prev_price) * 100

    week52_high: float = close.rolling(252).max().iloc[-1]
    week52_low: float = close.rolling(252).min().iloc[-1]

    print(f"\n📌 Price: ${current_price:.2f}  ({pct_change:+.2f}% today)")
    print(f"   52-Week High: ${week52_high:.2f}  |  52-Week Low: ${week52_low:.2f}")
    pct_from_high: float = ((current_price - week52_high) / week52_high) * 100
    print(f"   Distance from 52w High: {pct_from_high:.1f}%")

    # --- RSI ---
    rsi = calculate_rsi(close)
    rsi_val: float = rsi.iloc[-1]
    print(f"\n{'─'*55}")
    print(f"  RSI (14)         : {rsi_val:.1f}  →  {interpret_rsi(rsi_val)}")

    # --- MACD ---
    macd_line, signal_line, histogram = calculate_macd(close)
    macd_val: float = macd_line.iloc[-1]
    signal_val: float = signal_line.iloc[-1]
    hist_val: float = histogram.iloc[-1]
    print(f"  MACD             : {macd_val:.3f}  (Signal: {signal_val:.3f})")
    print(f"  → {interpret_macd(macd_val, signal_val, hist_val)}")

    # --- ADX ---
    adx, plus_di, minus_di = calculate_adx(high, low, close)
    adx_val: float = adx.iloc[-1]
    plus_di_val: float = plus_di.iloc[-1]
    minus_di_val: float = minus_di.iloc[-1]
    direction: str = "Bullish" if plus_di_val > minus_di_val else "Bearish"
    print(f"  ADX (14)         : {adx_val:.1f}  →  {interpret_adx(adx_val)}")
    print(f"  +DI: {plus_di_val:.1f}  |  -DI: {minus_di_val:.1f}  →  Direction: {direction}")

    # --- Stochastic ---
    k, d = calculate_stochastic(high, low, close)
    k_val: float = k.iloc[-1]
    d_val: float = d.iloc[-1]
    stoch_signal: str = "Overbought ⚠️" if k_val > 80 else ("Oversold ⚠️" if k_val < 20 else "Neutral ➡️")
    print(f"  Stochastic %K/%D : {k_val:.1f} / {d_val:.1f}  →  {stoch_signal}")

    # --- Rate of Change ---
    roc_10: float = calculate_roc(close, 10).iloc[-1]
    roc_20: float = calculate_roc(close, 20).iloc[-1]
    print(f"  ROC (10-day)     : {roc_10:+.2f}%")
    print(f"  ROC (20-day)     : {roc_20:+.2f}%")

    # --- Moving Averages ---
    ma50: float = close.rolling(50).mean().iloc[-1]
    ma200: float = close.rolling(200).mean().iloc[-1]
    ma_signal: str = "Golden Cross Zone 🌟" if ma50 > ma200 else "Death Cross Zone ⚠️"
    print(f"  MA50 / MA200     : ${ma50:.2f} / ${ma200:.2f}  →  {ma_signal}")

    # --- Volume Momentum ---
    avg_volume: float = volume.rolling(20).mean().iloc[-1]
    last_volume: float = volume.iloc[-1]
    vol_ratio: float = last_volume / avg_volume
    vol_signal: str = "Above Average 🔺" if vol_ratio > 1.2 else ("Below Average 🔻" if vol_ratio < 0.8 else "Normal ➡️")
    print(f"  Volume vs 20-avg : {vol_ratio:.2f}x  →  {vol_signal}")

    # --- OBV Trend ---
    sign: pd.Series = pd.Series(np.sign(close.diff()), index=close.index)
    obv: pd.Series = (sign * volume).fillna(0.0).cumsum()
    obv_trend: str = "Rising 📈" if obv.iloc[-1] > obv.iloc[-5] else "Falling 📉"
    print(f"  OBV Trend (5d)   : {obv_trend}")

    # --- Divergence check (basic) ---
    price_higher: bool = close.iloc[-1] > close.iloc[-10]
    rsi_higher: bool = rsi.iloc[-1] > rsi.iloc[-10]
    if price_higher and not rsi_higher:
        divergence = "⚠️  Bearish Divergence detected (price up, RSI down)"
    elif not price_higher and rsi_higher:
        divergence = "⚠️  Bullish Divergence detected (price down, RSI up)"
    else:
        divergence = "✅  No divergence detected"
    print(f"\n  Divergence Check : {divergence}")

    # --- Overall Momentum Summary ---
    bullish_signals: int = 0
    bearish_signals: int = 0

    if rsi_val > 50: bullish_signals += 1
    else: bearish_signals += 1

    if macd_val > signal_val: bullish_signals += 1
    else: bearish_signals += 1

    if plus_di_val > minus_di_val: bullish_signals += 1
    else: bearish_signals += 1

    if k_val > 50: bullish_signals += 1
    else: bearish_signals += 1

    if roc_10 > 0: bullish_signals += 1
    else: bearish_signals += 1

    if ma50 > ma200: bullish_signals += 1
    else: bearish_signals += 1

    print(f"\n{'─'*55}")
    print(f"  OVERALL MOMENTUM SCORE: {bullish_signals}/6 Bullish Signals")
    if bullish_signals >= 5:
        print("  Verdict: 🟢 STRONG BULLISH MOMENTUM")
    elif bullish_signals >= 4:
        print("  Verdict: 🟡 MODERATE BULLISH MOMENTUM")
    elif bullish_signals == 3:
        print("  Verdict: ⚪ MIXED / NEUTRAL MOMENTUM")
    elif bullish_signals >= 2:
        print("  Verdict: 🟠 MODERATE BEARISH MOMENTUM")
    else:
        print("  Verdict: 🔴 STRONG BEARISH MOMENTUM")

    print(f"{'='*55}\n")


# ── Run it ──────────────────────────────────────────────
if __name__ == "__main__":
    ticker = input("Enter stock ticker (e.g. AAPL, TSLA, NVDA): ").strip()
    analyze_momentum(ticker)