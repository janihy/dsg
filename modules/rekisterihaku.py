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


def get_emissions(licenseplate: str, rawresponse: bool = False) -> dict:
    return {}


def get_technical(licenseplate: str, backend: str = "motonet", rawresponse: bool = False) -> dict:
    techdata = {}
    if backend == "motonet":
        client = requests.session()
        r = client.get(MOTONET_BASE)

        soup = BeautifulSoup(r.text, features="lxml")
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
        data = json.loads(req.text)
        if rawresponse:
            print(json.dumps(data, indent=2))
            print(data)
        info = data.get('ajoneuvotiedot', [{}])[0]
        techdata = {
            'manufacturer': info.get('valmistaja'),
            'model': info.get('malli'),
            'type': info.get('tyyppi'),
            'year': "{vuosi}",
            'power': info.get('teho_kw'),
            'displacement': info.get('iskutilavuus'),
            'cylindercount': info.get('sylinterimaara'),
            'fueltype': info.get('polttoaine').lower(),
            'drivetype': data.get('vetotapa').lower(),
            'enginecode': info.get('moottorikoodit').replace(' ', ''),
            'vin': data.get('valmistenumero'),
            'suomiauto': True if data.get('maahantuotu') is None else False
        }

    else:
        raise Exception('not implemented yet :-(')
    return techdata


@module.commands('rekisteri')
@module.commands('rekkari')
@module.example(
    '!rekisteri bey-830',
    'BEY-830: VOLVO S40 II (MS) 2.0 D 2008. 100 kW 1998 cm³ 4-syl diesel etuveto (D4204T). Ajoneuvovero 609,55 EUR/vuosi, CO² 153 g/km (NEDC), kulutus 5,8/4,8/7,6 l/100 km. Oma/kokonaismassa 1459/1940 kg. Ensirekisteröinti 4.10.2007, VIN YV1MS754182368635, suomiauto',
    online=True)
def print_technical(bot, trigger):
    licenseplate = trigger.group(2)
    techdata = get_technical(licenseplate)
    emissionsdata = get_emissions(licenseplate)

    result = f"{licenseplate.upper()}: {techdata.get('manufacturer')} {techdata.get('model')} {techdata.get('type')} {techdata.get('year')}. {techdata.get('power')} kW {techdata.get('displacement')} cm³ {techdata.get('cylindercount')}-syl {techdata.get('fueltype')} {techdata.get('drivetype')} ({techdata.get('enginecode')}). Ajoneuvovero {emissionsdata.get('')} EUR/vuosi, CO²  {emissionsdata.get('')} g/km (NEDC), kulutus  {emissionsdata.get('')} l/ 100 km. Oma/kokonaismassa {emissionsdata.get('')} kg. Ensirekisteröinti {emissionsdata.get('')}, VIN {techdata.get('vin')}{', suomiauto' if techdata.get('suomiauto') else ''}"
    bot.say(result)


# BEY-830: VOLVO S40 II (MS) 2.0 D 2008. 100 kW 1998 cm³ 4-syl diesel etuveto (D4204T). Ajoneuvovero 609,55 EUR/vuosi, CO² 153 g/km (NEDC), kulutus 5,8/4,8/7,6 l/100 km. Oma/kokonaismassa 1459/1940 kg. Ensirekisteröinti 4.10.2007, VIN YV1MS754182368635, suomiauto


if __name__ == "__main__":
    from sopel.test_tools import run_example_tests
    run_example_tests(__file__)

    print(get_technical(licenseplate="bey-830"))
    print(get_technical(licenseplate="ilj-335"))
