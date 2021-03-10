# coding=utf-8
"""
    made by tuplis 2021
"""

from sopel.module import commands
from sopel.formatting import color, colors
from yfinance import Ticker


@commands('stonk')
def trigger(bot, trigger):
    if not trigger.group(2):
        bot.reply('sano vaikka !stonk tsla')
        return False
    try:
        info = Ticker(trigger.group(2)).info
        change = info.get('ask') - info.get('previousClose')
        changepercent = (change / info.get('previousClose')) * 100
        message = f'{info["shortName"]} ({info["symbol"].upper()}): {info["ask"]} {info["currency"]}'
        if change > 0:
            message += color(f' {change:g} ({changepercent:.4f} %) ↑', colors.GREEN)
        else:
            message += color(f' {change:g} ({changepercent:.4f} %) ↓', colors.RED)
    except Exception:
        bot.reply('hyvä kysymys, kysyppä joku toinen')
        return False
    bot.say(message)
