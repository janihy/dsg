# coding=utf8
"""
    made by tuplis 2021
"""
from __future__ import unicode_literals, absolute_import, division, print_function
from sopel import module

import requests
import json
import datetime
import re
from bs4 import BeautifulSoup

BILTEMA_ENDPOINT = 'https://reko.biltema.com/v1/Reko/carinfo/{licenseplate}/3/fi'
MOTONET_BASE = 'https://www.motonet.fi/'
MOTONET_ENDPOINT = MOTONET_BASE + 'fi/jsoncustomervehicle'
TRAFI_ENDPOINT = "https://autovertaamo.traficom.fi/trafienergiamerkki/{licenseplate}"
DEFAULT_HEADERS = {}


def configure(config):
    pass


def setup(bot):
    pass


def get_emissions(licenseplate: str, rawresponse: bool = False) -> dict:
    emissionsdata = {}
    headers = DEFAULT_HEADERS
    headers['Referer'] = "https://autovertaamo.traficom.fi/etusivu/index"
    req = requests.get(TRAFI_ENDPOINT.format(licenseplate=licenseplate), headers=headers)
    soup = BeautifulSoup(req.text, features="lxml")
    try:
        tax_elem = soup.find(text=re.compile('Vuotuinen ajoneuvovero'))
        emissionsdata['yearlytax'] = tax_elem.parent.find('h2').contents[0].strip()
        co2_elem = soup.find(text=re.compile('Esimerkkiauton CO'))
        emissionsdata['co2'] = co2_elem.parent.find('strong').contents[0].strip()
        consumption_elem = soup.find(text=re.compile('Polttoaineenkulutus'))
        emissionsdata['consumptions'] = [consumption.contents[0].strip() for consumption in consumption_elem.parent.parent.findAll('span')]
    except Exception:
        return None

    return emissionsdata


def get_technical(licenseplate: str, backend: str = "motonet", rawresponse: bool = False) -> dict:
    techdata = {}
    if backend == "motonet":
        client = requests.session()
        req = client.get(MOTONET_BASE)
        soup = BeautifulSoup(req.text, features="lxml")
        csrftoken = soup.find('input', {'name': 'CSRFTOKEN'}).get('value')

        payload = {
            "rekisterimaa": "FI",
            "-Rekisterinumerohaku": "true",
            "rekisterinumero": licenseplate
        }
        headers = DEFAULT_HEADERS
        headers['X-CSRF-TOKEN'] = csrftoken

        req = client.post(MOTONET_ENDPOINT, data=payload, headers=headers)
        data = json.loads(req.text)
        if rawresponse:
            print(json.dumps(data, indent=2))
        info = data.get('ajoneuvotiedot', [{}])[0]
        techdata = {
            'manufacturer': info.get('valmistaja'),
            'model': info.get('malli'),
            'type': info.get('tyyppi'),
            'year': None,
            'power': info.get('teho_kw'),
            'displacement': info.get('iskutilavuus'),
            'cylindercount': info.get('sylinterimaara'),
            'fueltype': info.get('polttoaine').lower(),
            'drivetype': data.get('vetotapa').lower(),
            'enginecode': info.get('moottorikoodit').replace(' ', ''),
            'registrationdate': datetime.datetime.strptime(data.get('ensirekisterointipvm'), '%Y-%m-%dT%H:%M:%SZ'),
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
    if emissionsdata is not None:
        emissionspart = f"Ajoneuvovero {emissionsdata.get('yearlytax')}, CO² {emissionsdata.get('co2')}, kulutus {'/'.join(emissionsdata.get('consumptions'))} l/100 km."
    else:
        emissionspart = "Ei päästö- tai verotietoja."

    result = f"{licenseplate.upper()}: {techdata.get('manufacturer')} {techdata.get('model')} {techdata.get('type')} {techdata.get('year')}. {techdata.get('power')} kW {techdata.get('displacement')} cm³ {techdata.get('cylindercount')}-syl {techdata.get('fueltype')} {techdata.get('drivetype')} ({techdata.get('enginecode')}). {emissionspart} Oma/kokonaismassa {techdata.get('')} kg. Ensirekisteröinti {techdata.get('registrationdate').strftime('%-d.%-m.%Y')}, VIN {techdata.get('vin')}{', suomiauto' if techdata.get('suomiauto') else ''}"
    bot.say(result)


if __name__ == "__main__":
    try:
        from sopel.test_tools import run_example_tests
        run_example_tests(__file__)
    except Exception:
        pass

    # print(get_emissions(licenseplate="bey-830"))
    # print(get_emissions(licenseplate="gfs-10"))
