# coding=utf8
"""
    made by tuplis 2021
"""
from __future__ import unicode_literals, absolute_import, division, print_function
from sopel import module

import requests
import json
from bs4 import BeautifulSoup

BILTEMA_ENDPOINT = 'https://reko.biltema.com/v1/Reko/carinfo/{licenseplate}/3/fi'
MOTONET_BASE = 'https://www.motonet.fi/'
MOTONET_ENDPOINT = MOTONET_BASE + 'fi/jsoncustomervehicle'
DEFAULT_HEADERS = {}


def configure(config):
    pass


def setup(bot):
    pass


def get_technical(licenseplate: str, backend: str = "motonet") -> dict:
    if backend == "motonet":
        result = {}
        client = requests.session()
        r = client.get(MOTONET_BASE)

        soup = BeautifulSoup(r.text)
        csrftoken = soup.find('input', {'name': 'CSRFTOKEN'}).get('value')

        payload = {
            "rekisterimaa": "FI",
            "-Rekisterinumerohaku": "true",
            "rekisterinumero": licenseplate
        }
        headers = DEFAULT_HEADERS
        headers['X-CSRF-TOKEN'] = csrftoken

        req = client.post(MOTONET_ENDPOINT, data=payload, headers=headers)
        # print(req.request.url)
        # print(req.request.headers)
        # print(req.request.body)
        print(req.text)

    else:
        raise Exception('not implemented yet :-(')
    return result


@module.commands('rekisteri')
@module.commands('rekkari')
@module.example(
    '!rekisteri bey-830',
    'BEY-830: VOLVO S40 II (MS) 2.0 D 2008. 100 kW 1998 cm³ 4-syl diesel etuveto (D4204T). Ajoneuvovero 609,55 EUR/vuosi, CO² 153 g/km (NEDC), kulutus 5,8/4,8/7,6 l/100 km. Oma/kokonaismassa 1459/1940 kg. Ensirekisteröinti 4.10.2007, VIN YV1MS754182368635, suomiauto',
    online=True)
def print_technical(bot, trigger):
    licenseplate = trigger.group(2).upper()

    result = f"{licenseplate}: "
    bot.say(result)


# BEY-830: VOLVO S40 II (MS) 2.0 D 2008. 100 kW 1998 cm³ 4-syl diesel etuveto (D4204T). Ajoneuvovero 609,55 EUR/vuosi, CO² 153 g/km (NEDC), kulutus 5,8/4,8/7,6 l/100 km. Oma/kokonaismassa 1459/1940 kg. Ensirekisteröinti 4.10.2007, VIN YV1MS754182368635, suomiauto


if __name__ == "__main__":
    from sopel.test_tools import run_example_tests
    run_example_tests(__file__)

    get_technical(licenseplate="bey-830")
