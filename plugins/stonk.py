# coding=utf-8
"""
made by tuplis 2021-2025
"""

import json
import re

import yfinance as yf
from pandas import DataFrame
from sopel.formatting import color, colors
from sopel.plugin import commands


def search_ticker(needle: str) -> str:
    """Search for possible tickers, prioritizing the helsinki stock market.
    Returns a symbol if found, otherwise an empty string."""
    quotes = yf.Search(f"{needle}", max_results=10).all.get("quotes", [])
    symbols = [q.get("symbol") for q in quotes if q.get("symbol")]
    if not symbols:
        return ""
    # prioritize tickers from the helsinki stock market, e.g. tyres -> tyres.he
    for symbol in symbols:
        if symbol.endswith(".HE"):
            return symbol
    return symbols[0]


def is_valid_ticker(symbol: str) -> bool:
    """Return True if the symbol resolves to an actually quoted instrument.
    yfinance returns an essentially empty info dict (and a 404) for bogus symbols."""
    try:
        info = yf.Ticker(symbol).info
    except Exception:
        return False
    return info.get("regularMarketPrice") is not None


def normalize_ticker(name: str) -> str:
    """Try to normalize a ticker name to something yfinance can understand better.
    This is due to ticker naming being inconsistent between different markets.
    Returns the normalized name, or the original name if no normalization was done."""
    name = name.upper()
    # if it already has a suffix, just return it
    if re.search(r"\.[A-Z]{1,4}$", name):
        return name
    # shortcut for some finnish stonks which have 1V naming pattern? no clue really
    if re.search(r"\dV$", name):
        return name + ".HE"

    # prioritize the helsinki stock market: if a ticker by this exact name is
    # listed there, use it (e.g. tyres -> tyres.he). yfinance's search often
    # won't surface helsinki listings at all, so we have to check directly.
    helsinki = f"{name}.HE"
    if is_valid_ticker(helsinki):
        return helsinki

    # no match, let's ask yfinance
    t = yf.Lookup(name).get_all(count=20)
    t = t.query("symbol.str.startswith(@name)")
    if len(t) == 0:
        ticker = search_ticker(name)
        if ticker:
            return normalize_ticker(ticker)
        return name

    # still prefer any helsinki listing among the matches
    he = t.query("symbol.str.endswith('.HE')")
    if len(he) > 0:
        return he.iloc[0].name

    # lol let's just return the first match if there are multiple
    # let's take a look later if this causes issues
    return t.iloc[0].name


def get_info(name: str):
    ticker_object = yf.Ticker(name)
    info = ticker_object.info
    return info


def get_prices(name: str, period: str = "ytd") -> DataFrame:
    # see https://github.com/ranaroussi/yfinance/blob/main/yfinance/base.py#L467 for valid periods
    ticker = yf.Ticker(name)
    prices = ticker.history(period)
    return prices


@commands("stonk")
def trigger(bot, trigger):
    if not trigger.group(2):
        bot.reply(f"Kokeile !{trigger.group(1)} TSLA")
        return False
    ticker = trigger.group(2)
    ticker = normalize_ticker(ticker)
    info = get_info(ticker)

    if not info:
        bot.reply("Valitettavasti meiltä on päässeet numerot loppumaan :/")
        return False
    try:
        # at some point these prices were not the delayed ones, not sure if this is still the case
        ytd_prices = get_prices(ticker, "ytd")
        year_first = ytd_prices["Open"].iloc[0]
        current_price = ytd_prices["Close"].iloc[-1]
        currency = info.get("currency") or info.get("financialCurrency")
        message = f"{info.get('longName')} ({ticker.upper()}): {current_price:.3f} {currency}."

        today = info.get("regularMarketChangePercent", 0) / 100
        if today > 0:
            indicator = colors.GREEN
        else:
            indicator = colors.RED
        message += " Tänään " + color(f"{today:+.2%}", indicator) + ","

        ytd = (current_price - year_first) / year_first
        year_low = ytd_prices["Low"].min()
        year_high = ytd_prices["High"].max()
        if ytd > 0:
            indicator = colors.GREEN
        else:
            indicator = colors.RED
        message += " YTD " + color(f"{ytd:+.2%}", indicator) + "."

        # pe can be "Infinity" or a number apparently
        pe = info.get("trailingPE")
        if isinstance(pe, (int, float)) and pe != float("inf"):
            message += f" P/E {pe:.2f}."

        dividendyield = info.get("dividendYield", 0) / 100 or None
        if dividendyield:
            message += f" Osinkotuotto {dividendyield:.2%}"
    except Exception as e:
        bot.reply(f"{repr(e)} :(")
        return False
    bot.say(message)


if __name__ == "__main__":
    # python3 stonk.py | jq --sort-keys .
    ticker = normalize_ticker("tyres")
    # print(ticker)
    print(json.dumps(dict(get_info(ticker))))
    stonks_to_normalize = [
        "ssh1v",
        "ssh1v.he",
        "nokia",
        "tyres",
        "nokia.he",
        "tsla",
        "aapl",
        "amzn",
        "msft",
        "googl",
        "iqqh",
    ]

    for stonk in stonks_to_normalize:
        print(f"trying to normalize: normalize_ticker({stonk}) -> {normalize_ticker(stonk)}")
