# coding=utf8
"""
    made by tuplis 2021
"""

from sopel import module, tools
from bs4 import BeautifulSoup
from typing import Dict, Optional

import requests
import json
import datetime
import re

BILTEMA_ENDPOINT = 'https://reko.biltema.com/v1/Reko/carinfo/{licenseplate}/3/fi'
MOTONET_BASE = 'https://www.motonet.fi/'
MOTONET_ENDPOINT = MOTONET_BASE + 'fi/jsoncustomervehicle'
TRAFI_ENDPOINT = "https://autovertaamo.traficom.fi/trafienergiamerkki/{licenseplate}"
DEFAULT_HEADERS: Dict[str, str] = {}


def configure(config):
    pass


def setup(bot):
    if 'nettix_token' not in bot.memory:
        bot.memory['nettix_token'] = tools.SopelMemory()


def refresh_nettix_token(bot) -> bool:
    res = requests.post('https://auth.nettix.fi/oauth2/token', data={'grant_type': 'client_credentials'})
    token = json.loads(res.text)
    bot.memory['nettix_token']['access_token'] = token.get('access_token', '')
    bot.memory['nettix_token']['expires_in'] = datetime.datetime.now() + datetime.timedelta(seconds=token.get('expires_in', ''))
    return res.status_code == 200


def get_nettix_link(bot, licenseplate) -> Optional[str]:
    if bot.memory['nettix_token'].get('expires_in', datetime.datetime.now()) <= datetime.datetime.now():
        if not refresh_nettix_token(bot):
            bot.say("oops, nettix api broken")

    headers = {
        "Accept": "application/json",
        "X-Access-Token": bot.memory['nettix_token'].get('access_token')
    }

    payload = {
        'identificationList': licenseplate
    }

    res = requests.get('https://api.nettix.fi/rest/car/search', params=payload, headers=headers)
    nettix_ad = json.loads(res.text)
    if nettix_ad:
        return nettix_ad[0].get('adUrl')
    else:
        return None


def get_tori_link(licenseplate: str) -> Optional[str]:
    payload = {
        'hakusana': licenseplate
    }

    res = requests.get('https://autot.tori.fi/vaihtoautot', params=payload)
    soup = BeautifulSoup(res.text, features="lxml")
    data = json.loads(soup.find('script', id="__NEXT_DATA__").string)

    try:
        # yeah i know
        link = data['props']['pageProps']['initialReduxState']['search']['result']['list_ads'][0]['share_link']
    except Exception:
        return None

    return link


def get_emissions(licenseplate: str, rawresponse: bool = False) -> Optional[dict]:
    emissionsdata = {}
    headers = DEFAULT_HEADERS
    headers['Referer'] = "https://autovertaamo.traficom.fi/etusivu/index"
    req = requests.get(TRAFI_ENDPOINT.format(licenseplate=licenseplate), headers=headers)
    soup = BeautifulSoup(req.text, features="lxml")
    try:
        tax_elem = soup.find(text=re.compile('Vuotuinen ajoneuvovero'))
        emissionsdata['yearlytax'] = tax_elem.parent.find('h3').contents[0].strip()
        co2_elem = soup.find(text=re.compile('Esimerkkiauton CO'))
        emissionsdata['co2'] = co2_elem.parent.find('strong').contents[0].strip()
        consumption_elem = soup.find(text=re.compile('Polttoaineenkulutus'))
        emissionsdata['consumptions'] = [consumption.contents[0].strip() for consumption in consumption_elem.parent.parent.findAll('span')]
    except Exception:
        return None

    return emissionsdata


def get_technical(licenseplate: str, rawresponse: bool = False) -> Optional[dict]:
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
    if data is None:
        data = {}
    motonet_info = data.get('ajoneuvotiedot', [{}])[0]

    req = client.get(BILTEMA_ENDPOINT.format(licenseplate=licenseplate))
    try:
        biltema_info = json.loads(req.text)
        if rawresponse:
            print(json.dumps(biltema_info, indent=2))
    except Exception:
        biltema_info = {}

    if motonet_info:
        firstreg = datetime.datetime.strptime(data.get('ensirekisterointipvm'), '%Y-%m-%dT%H:%M:%SZ')
    elif biltema_info:
        firstreg = datetime.datetime.strptime(biltema_info.get('registrationDate'), '%Y%m%d')
    else:
        # we can return and go home, most probably there was no data available
        return None

    techdata = {
        'manufacturer': motonet_info.get('valmistaja', ""),
        'model': motonet_info.get('malli', "") or biltema_info.get('nameOfTheCar'),
        'type': motonet_info.get('tyyppi', ""),
        'year': biltema_info.get('modelYear', None) or f'~{firstreg.year}',
        'power': motonet_info.get('teho_kw') or biltema_info.get('powerKw'),
        'displacement': motonet_info.get('iskutilavuus'),
        'cylindercount': motonet_info.get('sylinterimaara'),
        'fueltype': motonet_info.get('polttoaine', '').lower() if 'polttoaine' in motonet_info else data.get('polttoaine').lower(),
        'drivetype': data.get('vetotapa', '').lower(),
        'transmission': 'automaatti' if biltema_info.get('gearBox', '').lower() == 'automaattinen' else 'manuaali',
        'enginecode': motonet_info.get('moottorikoodit', '').replace(' ', '') or biltema_info.get('engineCode'),
        'weight': biltema_info.get('weightKg'),
        'maxweight': biltema_info.get('maxWeightKg'),
        'length': biltema_info.get('lenght'),
        'registrationdate': firstreg,
        'vin': data.get('valmistenumero') or biltema_info.get('chassieNumber'),
        'suomiauto': True if data.get('maahantuotu') is None else False and biltema_info.get('imported') == 'false'
    }

    return techdata


@module.commands('rekisteri')
@module.commands('rekkari')
@module.example(
    '!rekisteri bey-830',
    'BEY-830: VOLVO S40 II (MS) 2.0 D 2008. 100 kW 1998 cm³ 4-syl diesel etuveto (D4204T). Ajoneuvovero 609,55 EUR/vuosi, CO² 153 g/km (NEDC), kulutus 5,8/4,8/7,6 l/100 km. Oma/kokonaismassa 1459/1940 kg, pituus 4480 mm. Ensirekisteröinti 4.10.2007, VIN YV1MS754182368635, suomiauto',
    online=True)
def print_technical(bot, trigger) -> None:
    licenseplate = trigger.group(2)
    techdata = get_technical(licenseplate)
    if techdata is not None:
        emissionsdata = get_emissions(licenseplate)
        if emissionsdata is not None:
            emissionspart = f" Ajoneuvovero {emissionsdata.get('yearlytax')}, CO² {emissionsdata.get('co2')}, kulutus {'/'.join(emissionsdata.get('consumptions'))} l/100 km."
        else:
            emissionspart = " Ei päästö- tai verotietoja."
        if techdata.get('weight'):
            masspart = f" Oma/kokonaismassa {techdata.get('weight')}/{techdata.get('maxweight')} kg, pituus {techdata.get('length')} mm."
        else:
            masspart = ""
        result = f"{licenseplate.upper()}: {techdata.get('manufacturer')} {techdata.get('model')} {techdata.get('type')} {techdata.get('year')}. {techdata.get('power')} kW {techdata.get('displacement')} cm³ {techdata.get('cylindercount')}-syl {techdata.get('fueltype')} {techdata.get('transmission')} {techdata.get('drivetype')} ({techdata.get('enginecode')}).{emissionspart}{masspart} Ensirekisteröinti {techdata.get('registrationdate').strftime('%-d.%-m.%Y')}, VIN {techdata.get('vin')}{', suomiauto' if techdata.get('suomiauto') else ''}"
        bot.say(result)
    else:
        bot.say(f"{licenseplate.upper()}: Varmaan joku romu mihin ei saa enää ees varaosia :-(")

    ad_links = []
    nettiauto_url = get_nettix_link(bot, licenseplate)
    tori_url = get_tori_link(licenseplate)
    if nettiauto_url:
        ad_links.append(nettiauto_url)
    if tori_url:
        ad_links.append(tori_url)
    if ad_links:
        if techdata is not None:
            bot.say(f"On muuten myynnissä: {' ja '.join(ad_links)}")
        else:
            bot.say(f"On kuitenkin myynnissä: {' ja '.join(ad_links)}")


if __name__ == "__main__":
    try:
        from sopel.test_tools import run_example_tests
        run_example_tests(__file__)
    except Exception:
        pass

    # print(get_emissions(licenseplate="bey-830"))
    # print(get_emissions(licenseplate="gfs-10"))
    # print(get_nettix_token())
