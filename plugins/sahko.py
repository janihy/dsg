# coding=utf-8
"""
    made by tuplis 2022
"""

from sopel.plugin import commands
from datetime import datetime

import requests

PRICES_ENDPOINT = "https://api.porssisahko.net/v1/latest-prices.json"


def get_latest_prices():
    now = datetime.now().astimezone()
    prices = requests.get(PRICES_ENDPOINT).json()
    for price in prices.get('prices'):
        price['start'] = datetime.fromisoformat(price['startDate'].replace("Z", "+00:00"))
        price['end'] = datetime.fromisoformat(price['endDate'].replace("Z", "+00:00"))
        if price['start'] < now < price['end']:
            prices['current'] = price
    return prices


@commands('sähö')
def trigger(bot, trigger):
    bot.say(f"Sähkön börsähinta nyt {get_latest_prices().get('current').get('price')} snt/kWh")


if __name__ == '__main__':
    print(get_latest_prices().get('current'))
