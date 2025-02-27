# coding=utf-8
"""
    made by tuplis 2021
"""

from sopel.plugin import rule
import re

strings = [
    {
        'rule': 'via dolorosa',
        'response': 'https://www.youtube.com/watch?v=fvxWpQTjJ48'
    },
    {
        'rule': 'darekon',
        'response': 'https://imgur.com/a/oyrPJex'
    }
]


@rule(r'.*')
def trigger(bot, trigger):
    line = trigger.group(0)
    for string in strings:
        if re.search(string['rule'], line):
            bot.reply(f"{string['response']}")
