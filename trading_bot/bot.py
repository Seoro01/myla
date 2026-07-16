"""Stateless volatility-breakout trading bot for a single Upbit KRW market.

Designed to run unattended every ~10 minutes (see .github/workflows/trading-bot.yml).
State is derived from the real account balance each run, so no local state
file is needed and it's safe to run on ephemeral CI runners.

Rules:
  - No position held -> buy when price breaks (today's open + K * yesterday's range).
  - Position held -> sell on stop-loss (STOP_LOSS_PCT below average buy price)
    or unconditionally in the last minutes before midnight KST (day-end exit).

This is a simple, well-known rule set (a variant of the Larry Williams
volatility breakout strategy). It is not guaranteed to be profitable in any
given week and can lose money, including the full amount traded.
"""
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import pyupbit

TICKER = os.environ.get("TICKER", "KRW-BTC")
BUDGET_KRW = float(os.environ.get("BUDGET_KRW", "100000"))
K = float(os.environ.get("K", "0.5"))
STOP_LOSS_PCT = float(os.environ.get("STOP_LOSS_PCT", "0.10"))
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"

MIN_ORDER_KRW = 5000
DUST_KRW = 5000
LOG_PATH = os.environ.get("LOG_PATH", os.path.join(os.path.dirname(__file__), "trades.csv"))


def log_trade(action, price, amount_krw, note=""):
    header_needed = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        if header_needed:
            f.write("timestamp,ticker,action,price,amount_krw,note\n")
        ts = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        f.write(f"{ts},{TICKER},{action},{price:.0f},{amount_krw:.0f},{note}\n")


def is_near_day_end(now_kst):
    return now_kst.hour == 23 and now_kst.minute >= 50


def get_target_price(ticker, k):
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    if df is None or len(df) < 2:
        return None
    yesterday = df.iloc[-2]
    today_open = df.iloc[-1]["open"]
    return today_open + (yesterday["high"] - yesterday["low"]) * k


def get_avg_buy_price(upbit, ticker):
    currency = ticker.split("-")[1]
    for b in upbit.get_balances():
        if b["currency"] == currency:
            return float(b["avg_buy_price"])
    return None


def main():
    now_kst = datetime.now(ZoneInfo("Asia/Seoul"))

    current_price = pyupbit.get_current_price(TICKER)
    if current_price is None:
        print("Could not fetch current price, skipping this run.")
        return

    print(f"[{now_kst.isoformat()}] DRY_RUN={DRY_RUN} ticker={TICKER} price={current_price}")

    if DRY_RUN:
        upbit = None
        krw_balance = BUDGET_KRW
        coin_balance = 0.0
        avg_price = None
    else:
        if not os.environ.get("UPBIT_ACCESS_KEY") or not os.environ.get("UPBIT_SECRET_KEY"):
            print("Missing UPBIT_ACCESS_KEY/UPBIT_SECRET_KEY secrets.")
            sys.exit(1)
        upbit = pyupbit.Upbit(os.environ["UPBIT_ACCESS_KEY"], os.environ["UPBIT_SECRET_KEY"])
        krw_balance = upbit.get_balance("KRW") or 0.0
        coin_balance = upbit.get_balance(TICKER) or 0.0
        avg_price = get_avg_buy_price(upbit, TICKER)

    coin_value = coin_balance * current_price

    if coin_value < DUST_KRW:
        target = get_target_price(TICKER, K)
        if target is None:
            print("Could not compute target price, skipping.")
            return
        print(f"no position. target={target:.0f} current={current_price:.0f}")

        if current_price >= target and not is_near_day_end(now_kst):
            buy_krw = min(krw_balance, BUDGET_KRW) * 0.9995
            if buy_krw < MIN_ORDER_KRW:
                print(f"buy signal but available budget {buy_krw:.0f} KRW is below minimum order size.")
                return
            print(f"BUY signal: {buy_krw:.0f} KRW at {current_price:.0f}")
            if DRY_RUN:
                log_trade("DRY_BUY", current_price, buy_krw, "breakout")
            else:
                upbit.buy_market_order(TICKER, buy_krw)
                log_trade("BUY", current_price, buy_krw, "breakout")
        else:
            print("no buy signal.")
    else:
        reference_price = avg_price if avg_price else current_price
        change = (current_price - reference_price) / reference_price
        should_stop = change <= -STOP_LOSS_PCT
        should_day_end = is_near_day_end(now_kst)
        print(f"holding position. avg_buy={reference_price:.0f} current={current_price:.0f} change={change * 100:.2f}%")

        if should_stop or should_day_end:
            reason = "stop_loss" if should_stop else "day_end"
            print(f"SELL signal: {reason}")
            if DRY_RUN:
                log_trade("DRY_SELL", current_price, coin_value, reason)
            else:
                upbit.sell_market_order(TICKER, coin_balance)
                log_trade("SELL", current_price, coin_value, reason)
        else:
            print("holding, no sell signal.")


if __name__ == "__main__":
    main()
