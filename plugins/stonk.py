# coding=utf-8
"""
    made by tuplis 2021-2023
"""

from sopel.plugin import commands
from sopel.formatting import color, colors
import json
import yfinance


def get_info(name: str, fast: bool = True) -> yfinance.scrapers.quote.InfoDictWrapper:
    ticker_object = yfinance.Ticker(name)
    try:
        info = ticker_object.info
        assert info.get("shortName")
    except Exception:
        if name[-3:].lower() != ".he":
            if '.' in name:
                # user probably wrote the name wrong
                return get_info(f'{name.replace(".", "-")}', fast)
            # if not, maybe they forgot the helsinki börs (.he)
            return get_info(f"{name}.he", fast)
        return None
    return info


def get_prices(ticker: str, period: str = "ytd") -> dict:
    # see https://github.com/ranaroussi/yfinance/blob/main/yfinance/base.py#L467 for valid periods
    # FIXME: move the .he suffix guess to somewhere usable in both here and get_info
    ticker = yfinance.Ticker(ticker)
    prices = ticker.history(period)
    return prices


@commands('stonk', 'superstonk')
def trigger(bot, trigger):
    if not trigger.group(2):
        bot.reply(f'Kokeile !{trigger.group(1)} TSLA')
        return False
    ticker = trigger.group(2)
    if trigger.group(1) == 'stonk':
        fast = True
    else:
        fast = False
    info = get_info(ticker, fast)

    if not info:
        bot.reply('Valitettavasti meiltä on päässeet numerot loppumaan :/')
        return False
    try:
        if fast:
            change = info.get('bid') - info.get('previousClose')
            changepercent = (change / info.get('previousClose'))
            message = f'{ticker.upper()}: {info["bid"]:.2f} {info["currency"]}'
            prices = get_prices(ticker, "1d")
            day_high = prices["High"].iloc[-1]
            day_low = prices["Low"].iloc[-1]
            if change > 0:
                message += color(f' {change:+.2f} ({changepercent:+.4%}) {"🚀" if changepercent > 0.02 else "↑"}', colors.GREEN)
            else:
                message += color(f' {change:+.2f} ({changepercent:+.4%}) ↓', colors.RED)
            message += f' Päivän ylin {day_high:.2f}, alin {day_low:.2f}'
        else:
            ytd_prices = get_prices(ticker, "ytd")
            year_first = ytd_prices["Open"].iloc[0]
            last_price = ytd_prices["Close"].iloc[-1]
            message = f'{info.get("shortName")} ({ticker.upper()}): {last_price:.2f} {info["financialCurrency"]}.'

            ytd = (last_price - year_first) / year_first
            if ytd > 0:
                indicator = colors.GREEN
            else:
                indicator = colors.RED
            message += color(f' YTD {ytd:+.2%}.', indicator)

            year_low = ytd_prices["Low"].min()
            year_high = ytd_prices["High"].max()
            message += f' Vuoden ylin {year_high:.2f}, alin {year_low:.2f}.'

            pe = info.get("trailingPE")
            if pe:
                message += f' P/E {pe:.2f}.'

            dividendyield = info.get("dividendYield") or None
            if dividendyield:
                message += f" Osinkotuotto {dividendyield:.2%}"
    except Exception as e:
        bot.reply(f"{repr(e)} :(")
        return False
    bot.say(message)


if __name__ == '__main__':
    # python3 stonk.py | jq --sort-keys .
    print(json.dumps(dict(get_info("tsla", fast=False))))
