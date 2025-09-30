# coding=utf-8
"""
    made by tuplis 2021-2025
"""

from sopel.plugin import commands
from sopel.formatting import color, colors
from pandas import DataFrame
import json
import re
import yfinance as yf


def search_ticker(needle: str) -> str:
    '''Search for possible tickers, return one if found'''
    data = yf.Search(f"{needle}", max_results=1).all
    return data.get('quotes', [])[0].get('symbol')


def normalize_ticker(name: str) -> str:
    '''Try to normalize a ticker name to something yfinance can understand better.
    This is due to ticker naming being inconsistent between different markets.
    Returns the normalized name, or the original name if no normalization was done.'''
    name = name.upper()
    # if it already has a suffix, just return it
    if re.search(r"\.[A-Z]{1,4}$", name):
        return name
    # shortcut for some finnish stonks which have 1V naming pattern? no clue really
    if re.search(r"\dV$", name):
        return name + ".HE"

    # no match, let's ask yfinance
    t = yf.Lookup(name).get_all(count=5)
    t = t.query('symbol.str.startswith(@name)')
    if len(t) == 0:
        ticker = search_ticker(name)
        if ticker:
            return normalize_ticker(ticker)
    if len(t) == 1:
        return t.iloc[0].name

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


@commands('stonk')
def trigger(bot, trigger):
    if not trigger.group(2):
        bot.reply(f'Kokeile !{trigger.group(1)} TSLA')
        return False
    ticker = trigger.group(2)
    ticker = normalize_ticker(ticker)
    info = get_info(ticker)

    if not info:
        bot.reply('Valitettavasti meiltä on päässeet numerot loppumaan :/')
        return False
    try:
        ytd_prices = get_prices(ticker, "ytd")
        year_first = ytd_prices["Open"].iloc[0]
        yesterday_price = ytd_prices["Close"].iloc[-2]
        current_price = ytd_prices["Close"].iloc[-1]
        currency = info.get("financialCurrency") or info.get("currency")
        message = f'{info.get("shortName")} ({ticker.upper()}): {current_price:.3f} {currency}.'

        today = (current_price - yesterday_price) / yesterday_price
        if today > 0:
            indicator = colors.GREEN
        else:
            indicator = colors.RED
        message += color(f' Tänään {today:+.2%}.', indicator)

        ytd = (current_price - year_first) / year_first
        if ytd > 0:
            indicator = colors.GREEN
        else:
            indicator = colors.RED
        message += color(f' YTD {ytd:+.2%}.', indicator)

        year_low = ytd_prices["Low"].min()
        year_high = ytd_prices["High"].max()
        message += f' Vuoden ylin {year_high:.2f}, alin {year_low:.2f}.'

        # pe can be "Infinity" or a number apparently
        pe = info.get("trailingPE")
        if isinstance(pe, (int, float)) and pe != float('inf'):
            message += f' P/E {pe:.2f}.'

        dividendyield = info.get("dividendYield", 0) / 100 or None
        if dividendyield:
            message += f" Osinkotuotto {dividendyield:.2%}"
    except Exception as e:
        bot.reply(f"{repr(e)} :(")
        return False
    bot.say(message)


if __name__ == '__main__':
    # python3 stonk.py | jq --sort-keys .
    # print(json.dumps(dict(get_info("ssh1v.he"))))
    stonks_to_normalize = [
        "ssh1v",
        "ssh1v.he",
        "nokia",
        "nokia.he",
        "tsla",
        "aapl",
        "amzn",
        "msft",
        "googl",
        "iqqh"
    ]

    for stonk in stonks_to_normalize:
        print(f"trying to normalize: normalize_ticker({stonk}) -> {normalize_ticker(stonk)}")
