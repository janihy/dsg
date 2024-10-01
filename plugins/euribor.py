# coding=utf-8
"""
    made by tuplis 2024
"""

# Euribor
# https://www.suomenpankki.fi/fi/Tilastot/korot/taulukot2/

from sopel.plugin import command

import requests
import xml.etree.ElementTree as ET

EURIBOR_ENDPOINT = "https://www.suomenpankki.fi/WebForms/ReportViewerPage.aspx?report=/tilastot/markkina-_ja_hallinnolliset_korot/euribor_korot_today_xml_fi&output=xml"


def get_euribor_rates():
    try:
        # Fetch 3-month Euribor data
        response = requests.get(EURIBOR_ENDPOINT)
        response.raise_for_status()  # Raise an error for failed requests
        rates = {}
        root = ET.fromstring(response.content).findall('.//period/matrix1_Title_Collection/', {'': 'euribor_korot_today_xml_fi'})
        for child in root:
            rate = {child.get('name'): child.find('./{euribor_korot_today_xml_fi}intr').get('value')}
            rates.update(rate)

        return rates

    except Exception as e:
        print(e)
    return None


@command('euribor')
def production(bot, trigger):
    data = get_euribor_rates()
    bot.say(data)
