# coding=utf-8
"""
    made by tuplis 2022
"""

# Fingrid sähköjärjestelmän tila
# https://www.fingrid.fi/sahkomarkkinat/sahkojarjestelman-tila/
# ID map  https://data.fingrid.fi/open-data-forms/search/en/
# API     https://data.fingrid.fi/fi/pages/api

from sopel.plugin import commands
from datetime import datetime
from typing import Dict

import requests

PRICES_ENDPOINT = "https://api.porssisahko.net/v1/latest-prices.json"
FINGRID_ENDPOINT = "https://api.fingrid.fi/v1/variable/event/json"
FINGRID_ID_MAP = {
    "181": "tuulivoima",
    "188": "ydinvoima",
    "191": "vesivoima",
    "192": "yhteensä",
}


def get_current_output() -> Dict[int, float]:
    values = {}
    id_list = FINGRID_ID_MAP.keys()
    data = requests.get(f"{FINGRID_ENDPOINT}/{','.join(id_list)}").json()
    values = {str(prop.get("variable_id")): prop.get("value") for prop in data}
    return values


def build_output_msg(data) -> str:
    msg = f"Jytkyttää yhteensä {data.get('192')} MW: "
    id_list = ["188", "181", "191"]
    parts = []
    for prod_type in id_list:
        parts.append(f"{FINGRID_ID_MAP[prod_type]} {data.get(prod_type)} MW")
    msg += ", ".join(parts)
    msg += "."
    return msg


def get_latest_prices() -> Dict[str,dict]:
    now = datetime.now().astimezone()
    prices = requests.get(PRICES_ENDPOINT).json()
    for price in prices.get('prices'):
        price['start'] = datetime.fromisoformat(price['startDate'].replace("Z", "+00:00"))
        price['end'] = datetime.fromisoformat(price['endDate'].replace("Z", "+00:00"))
        if price['start'] < now < price['end']:
            prices['current'] = price
    return prices


@commands('sähö', 'sähkö', 'pörssisähkö')
def prices(bot, trigger):
    bot.say(f"Pörssisähkö nyt {get_latest_prices().get('current').get('price')} snt/kWh")


@commands('tuotanto', 'jytkytys', 'jytkyttää')
def production(bot, trigger):
    data = get_current_output()
    bot.say(build_output_msg(data))


@commands('ol3')
def ol3(bot, trigger):
    bot.say("I want to believe")


if __name__ == '__main__':
    # print(get_latest_prices().get('current'))
    print(build_output_msg(get_current_output()))
