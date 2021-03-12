# coding=utf-8
"""
    made by tuplis 2021
"""

from sopel.module import rule
import re

strings = [
    {
        'rule': 'via dolorosa',
        'response': 'https://soundcloud.com/oaklydnb/tommi-lantinen-via-dolorosa-oakly-bootleg'
    }
]


@rule(r'.*')
def trigger(bot, trigger):
    line = trigger.group(0)
    for string in strings:
        if re.search(string['rule'], line):
            bot.reply(f"{string['response']}")
