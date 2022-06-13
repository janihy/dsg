# coding=utf-8
"""
    made by tuplis 2021
"""

from sopel.plugin import commands
from sopel.formatting import color, colors
from yfinance import Ticker


def get_ticker(name: str) -> Ticker:
    ticker = Ticker(name)
    info = ticker.info
    if not info.get("ask"):
        if name[-3:] != ".HE":
            if '.' in name:
                # user probably wrote the name wrong
                return get_ticker(f'{name.replace(".", "-")}')
            # if not, maybe they forgot the helsinki börs (.he)
            return get_ticker(f"{name}.HE")
        return False
    # print(ticker.dividends)

    return ticker


@commands('stonk')
def trigger(bot, trigger):
    if not trigger.group(2):
        bot.reply('Kokeile !stonk tsla')
        return False
    name = trigger.group(2).upper()
    ticker = get_ticker(name)
    if not ticker:
        bot.reply('Valitettavasti meiltä on päässeet numerot loppumaan :/')
        return False
    try:
        info = ticker.info
        if name != info.get("symbol", ""):
            bot.reply(f"Semmosta ei oo, mutta kelpaako {info.get('symbol')}:")
        change = info.get('ask') - info.get('previousClose')
        changepercent = (change / info.get('previousClose')) * 100
        message = f'{info["shortName"]} ({info["symbol"].upper()}): {info["ask"]} {info["currency"]}'
        if change > 0:
            message += color(f' {change:g} ({changepercent:.4f} %) ↑', colors.GREEN)
        else:
            message += color(f' {change:g} ({changepercent:.4f} %) ↓', colors.RED)
    except Exception as e:
        bot.reply(f"{repr(e)} :(")
        return False
    bot.say(message)


if __name__ == '__main__':
    stonk = get_ticker('tsla')
    print(stonk.info)
