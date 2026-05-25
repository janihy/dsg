# coding=utf-8
"""
    made by tuplis 2024
"""

# Euribor
# https://www.suomenpankki.fi/fi/tilastot/korot-ja-valuuttakurssit/euriborkorot/

from sopel import db
from sopel.plugin import command
from decimal import Decimal

import re
import requests
import xml.etree.ElementTree as ET

EURIBOR_ENDPOINT = "https://reports.suomenpankki.fi/WebForms/ReportViewerPage.aspx?report=/tilastot/markkina-_ja_hallinnolliset_korot/euribor_korot_today_xml_fi&output=xml"


def get_euribor_rates():
    try:
        # Fetch 3-month Euribor data
        response = requests.get(EURIBOR_ENDPOINT)
        response.raise_for_status()  # Raise an error for failed requests
        rates = {}
        root = ET.fromstring(response.content).findall('.//matrix1_Title_Collection/', {'': 'euribor_korot_today_xml_fi'})
        for child in root:
            rate = {re.sub(r'^([0-9]+\s[a-z]+) \(tod\.pv/360\)$', r'\1', child.get('name')): child.find('./{euribor_korot_today_xml_fi}intr').get('value').replace(',', '.')}
            rates.update(rate)
        return rates

    except Exception as e:
        print(e)
    return None


def euribor_data_to_str(data):
    rates = f"12 kk: {data['12 kk']} ja 3 kk: {data['3 kk']}"
    if "margin" in data:
        margin = Decimal(str(data["margin"]))
        data = {k: str(Decimal(v) + margin) for k, v in data.items() if k != "margin"}
        rates += f", mutta sulle {data['12 kk']} ja {data['3 kk']}"
    return rates


@command('euribor')
def say_euribor(bot, trigger):
    data = get_euribor_rates()
    state = db.SopelDB(bot.config)
    if trigger.group(2):
        margin = float(trigger.group(2))
        state.set_nick_value(trigger.nick, 'euribor_margin', margin)
    else:
        margin = state.get_nick_value(trigger.nick, 'euribor_margin')
    if margin:
        data["margin"] = margin
    out = euribor_data_to_str(data)
    bot.say(out)
