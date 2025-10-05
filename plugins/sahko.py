# coding=utf-8
"""
    made by tuplis 2022
"""

# Fingrid sähköjärjestelmän tila
# https://www.fingrid.fi/sahkomarkkinat/sahkojarjestelman-tila/
# ID map  https://data.fingrid.fi/open-data-forms/search/en/
# API     https://data.fingrid.fi/fi/pages/api

from sopel.plugin import commands
from sopel.formatting import color, colors
from datetime import datetime, timedelta
from typing import Dict
import json

import requests
from bs4 import BeautifulSoup

PRICES_ENDPOINT = "https://api.porssisahko.net/v2/latest-prices.json"
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


def get_latest_prices() -> Dict[str, dict]:
    now = datetime.now().astimezone()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    tomorrow_end = tomorrow_start + timedelta(days=1)
    raw_prices = requests.get(PRICES_ENDPOINT).json().get('prices')
    prices = {}
    today_data = []
    tomorrow_data = []

    for i, price in enumerate(raw_prices):
        price['start'] = datetime.fromisoformat(price.pop('startDate'))
        price['end'] = datetime.fromisoformat(price.pop('endDate'))
        if price['start'] < now < price['end']:
            prices['current'] = raw_prices[i].get("price")
            # the data has been ordered so trust me bro
            prices['next_tick'] = raw_prices[i-1].get("price")
        if price['start'] >= today_start and price['end'] <= tomorrow_start:
            today_data.append(price)
        elif price['start'] >= tomorrow_start and price['end'] <= tomorrow_end:
            tomorrow_data.append(price)

    tomorrow_prices = [price.get('price') for price in tomorrow_data]
    prices['tomorrow'] = {
        'min': round(min(tomorrow_prices), 2),
        'max': round(max(tomorrow_prices), 2),
        'average': round(sum(tomorrow_prices) / len(tomorrow_prices), 2),
        'prices': tomorrow_data,
        'is_data_complete': len(tomorrow_prices) == 96
    }

    today_prices = [price.get('price') for price in today_data]
    prices['today'] = {
        'min': round(min(today_prices), 2),
        'max': round(max(today_prices), 2),
        'average': round(sum(today_prices) / len(today_prices), 2),
        'prices': today_data,
        'is_data_complete': len(today_prices) == 96
    }

    return prices


def olkiluoto():
    # response = requests.get("https://toimiikoolkiluoto3.fi/", timeout=3)

    # if response.status_code == 200:
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     status = soup.find('h1')

    #     if status:
    #         return status.get_text()

    return "I want to believe"


@commands('sähö', 'sähkö', 'pörssisähkö')
def prices(bot, trigger):
    prices = get_latest_prices()
    if trigger.group(2) == "huomenna":
        tomorrow = prices.get('tomorrow')
        tomorrow_min = tomorrow.get('min')
        tomorrow_max = tomorrow.get('max')
        response = f"Börs huomenna: alin/ylin {tomorrow_min}/{tomorrow_max} ja keskihinta {tomorrow.get('average')} snt/kWh."
        if not tomorrow.get('is_data_complete'):
            response += " Hinnat tosin tulee vasta klo 14."
        bot.say(response)
    else:
        current_price = prices.get('current')
        next_tick = prices.get('next_tick')
        today = prices.get('today', {})
        today_average = today.get('average')
        current_price_str = color(str(current_price), colors.GREEN) if current_price < today_average else color(str(current_price), colors.RED)
        current_trend_icon = "📈" if next_tick > current_price else "📉"
        bot.say(f"Pörssisähkö nyt {current_price_str} snt/kWh {current_trend_icon}. Päivän alin/ylin {today.get('min')}/{today.get('max')} ja keskihinta {round(today_average, 2)} snt/kWh.")

        # hehz
        if current_price >= 50:
            bot.say("Gallis")


@commands('tuotanto', 'jytkytys', 'jytkyttää')
def production(bot, trigger):
    data = get_current_output()
    bot.say(build_output_msg(data))


@commands('ol3')
def ol3(bot, trigger):
    bot.say(olkiluoto())


if __name__ == '__main__':
    #print(get_latest_prices().get('current'))
    #print(build_output_msg(get_current_output()))
    print(json.dumps(get_latest_prices(), indent=2, default=str))
