# coding=utf-8
"""
made by tuplis 2024
"""

# Euribor
# https://www.suomenpankki.fi/fi/tilastot/korot-ja-valuuttakurssit/euriborkorot/

import re
import xml.etree.ElementTree as ET
from decimal import Decimal

import requests
from sopel import db
from sopel.plugin import command

EURIBOR_ENDPOINT = "https://reports.suomenpankki.fi/WebForms/ReportViewerPage.aspx?report=/tilastot/markkina-_ja_hallinnolliset_korot/euribor_korot_today_xml_fi&output=xml"


def get_euribor_rates():
    try:
        # Fetch 3-month Euribor data
        response = requests.get(EURIBOR_ENDPOINT)
        response.raise_for_status()  # Raise an error for failed requests
        rates = {}
        ns = {"": "euribor_korot_today_xml_fi"}
        tree = ET.fromstring(response.content)
        period = tree.find(".//{euribor_korot_today_xml_fi}period")
        date = period.get("value") if period is not None else None
        root = tree.findall(".//matrix1_Title_Collection/", ns)
        for child in root:
            rate = {
                re.sub(r"^([0-9]+\s[a-z]+) \(tod\.pv/360\)$", r"\1", child.get("name")): child.find(
                    "./{euribor_korot_today_xml_fi}intr"
                )
                .get("value")
                .replace(",", ".")
            }
            rates.update(rate)
        return (rates, date)

    except Exception as e:
        print(e)
    return None


def euribor_data_to_str(data, date=None):
    prefix = f"Euribor ({date}): " if date else "Euribor: "
    rates = f"12 kk: {data['12 kk']} ja 3 kk: {data['3 kk']}"
    if "margin" in data:
        margin = Decimal(str(data["margin"]))
        data = {k: str(Decimal(v) + margin) for k, v in data.items() if k != "margin"}
        rates += f", mutta sulle {data['12 kk']} ja {data['3 kk']}"
    return prefix + rates


@command("euribor")
def say_euribor(bot, trigger):
    result = get_euribor_rates()
    if result is None:
        bot.say("Euribor-korkojen haku epäonnistui.")
        return
    data, date = result
    state = db.SopelDB(bot.config)
    if trigger.group(2):
        margin = float(trigger.group(2))
        state.set_nick_value(trigger.nick, "euribor_margin", margin)
    else:
        margin = state.get_nick_value(trigger.nick, "euribor_margin")
    if margin:
        data["margin"] = margin
    out = euribor_data_to_str(data, date)
    bot.say(out)
