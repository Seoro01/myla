#!/usr/bin/env python3
"""Pulls current price/change (+ US news headlines) for each holding in portfolio.yaml.

Usage: python scripts/fetch_market_data.py [path/to/portfolio.yaml]
Prints a JSON report to stdout and writes it to output/<date>.json.
"""
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def fetch_kr(ticker: str) -> dict:
    from pykrx import stock

    today = date.today()
    start = today - timedelta(days=14)
    df = stock.get_market_ohlcv_by_date(start.strftime("%Y%m%d"), today.strftime("%Y%m%d"), ticker)
    if df.empty or len(df) < 1:
        raise RuntimeError(f"no OHLCV data for {ticker}")

    last = df.iloc[-1]
    prev_close = float(df.iloc[-2]["종가"]) if len(df) >= 2 else float(last["시가"])
    price = float(last["종가"])
    change = price - prev_close
    change_pct = (change / prev_close * 100) if prev_close else 0.0

    return {
        "price": price,
        "prev_close": prev_close,
        "change": change,
        "change_pct": change_pct,
        "volume": int(last["거래량"]),
        "as_of": str(df.index[-1].date()),
    }


def fetch_us(ticker: str) -> dict:
    import yfinance as yf

    t = yf.Ticker(ticker)
    hist = t.history(period="5d")
    if hist.empty:
        raise RuntimeError(f"no history data for {ticker}")

    price = float(hist["Close"].iloc[-1])
    prev_close = float(hist["Close"].iloc[-2]) if len(hist) >= 2 else float(hist["Open"].iloc[-1])
    change = price - prev_close
    change_pct = (change / prev_close * 100) if prev_close else 0.0

    news_items = []
    try:
        for item in (t.news or [])[:3]:
            content = item.get("content", item)
            news_items.append(
                {
                    "title": content.get("title"),
                    "publisher": (content.get("provider") or {}).get("displayName")
                    or content.get("publisher"),
                    "link": (content.get("canonicalUrl") or {}).get("url") or content.get("link"),
                }
            )
    except Exception:
        pass

    return {
        "price": price,
        "prev_close": prev_close,
        "change": change,
        "change_pct": change_pct,
        "volume": int(hist["Volume"].iloc[-1]),
        "as_of": str(hist.index[-1].date()),
        "news": news_items,
    }


def main():
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "portfolio.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    results = []
    for h in config["holdings"]:
        market = h["market"].upper()
        entry = {"market": market, "ticker": h["ticker"], "name": h.get("name", h["ticker"])}
        try:
            data = fetch_kr(h["ticker"]) if market == "KR" else fetch_us(h["ticker"])
            entry.update(data)
            qty, avg_price = h.get("quantity"), h.get("avg_price")
            if qty and avg_price:
                entry["market_value"] = data["price"] * qty
                entry["unrealized_pnl"] = (data["price"] - avg_price) * qty
                entry["unrealized_pnl_pct"] = (data["price"] - avg_price) / avg_price * 100
                entry["quantity"] = qty
                entry["avg_price"] = avg_price
        except Exception as e:
            entry["error"] = str(e)
        results.append(entry)

    report = {"generated_at": datetime.now().isoformat(), "holdings": results}

    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / f"{date.today().isoformat()}.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
