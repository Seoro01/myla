"""Quick offline backtest for the volatility-breakout strategy used by bot.py.

Not investment advice — this only replays historical daily candles to give a
rough sense of how the rule set would have performed. Real results will
differ due to slippage, partial fills, and market regime changes.
"""
import os

import pandas as pd
import pyupbit

TICKER = os.environ.get("TICKER", "KRW-BTC")
K = float(os.environ.get("K", "0.5"))
STOP_LOSS_PCT = float(os.environ.get("STOP_LOSS_PCT", "0.10"))
FEE = 0.0005  # upbit taker fee ~0.05%
BUDGET = float(os.environ.get("BUDGET_KRW", "100000"))
DAYS = int(os.environ.get("BACKTEST_DAYS", "200"))


def run():
    df = pyupbit.get_ohlcv(TICKER, interval="day", count=DAYS)
    df["prev_range"] = df["high"].shift(1) - df["low"].shift(1)
    df["target"] = df["open"] + df["prev_range"] * K

    capital = BUDGET
    trades = []

    for i in range(1, len(df)):
        row = df.iloc[i]
        target = row["target"]
        if pd.isna(target):
            continue
        if row["high"] < target:
            continue
        buy_price = target
        stop_price = buy_price * (1 - STOP_LOSS_PCT)
        sell_price = stop_price if row["low"] <= stop_price else row["close"]
        gross_ret = sell_price / buy_price
        net_ret = gross_ret * (1 - FEE) * (1 - FEE) - 1
        capital *= 1 + net_ret
        trades.append((str(row.name.date()), round(buy_price), round(sell_price), round(net_ret * 100, 2)))

    print(f"ticker={TICKER} k={K} stop_loss={STOP_LOSS_PCT} days_tested={len(df)}")
    print(f"trades executed: {len(trades)}")
    for date, buy, sell, ret in trades[-20:]:
        print(f"  {date}: buy={buy} sell={sell} ret={ret}%")
    print(f"final capital from {BUDGET:.0f}: {capital:.0f} KRW ({(capital / BUDGET - 1) * 100:.2f}%)")

    # also show last 7 calendar days worth of trades as a "would this week have worked" sample
    last7 = trades[-7:]
    if last7:
        week_capital = BUDGET
        for _, _, _, ret in last7:
            week_capital *= 1 + ret / 100
        print(f"\nlast {len(last7)} trades only (rough 'one week' sample): "
              f"{BUDGET:.0f} -> {week_capital:.0f} KRW ({(week_capital / BUDGET - 1) * 100:.2f}%)")


if __name__ == "__main__":
    run()
