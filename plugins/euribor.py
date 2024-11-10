# coding=utf-8
"""
    made by tuplis 2024
"""

# Euribor
# https://www.suomenpankki.fi/fi/tilastot/korot-ja-valuuttakurssit/euriborkorot/

from sopel.plugin import command

import requests
import xml.etree.ElementTree as ET

EURIBOR_ENDPOINT = "https://reports.suomenpankki.fi/WebForms/ReportViewerPage.aspx?report=/tilastot/markkina-_ja_hallinnolliset_korot/euribor_korot_today_xml_fi&output=xml"


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


def euribor_data_to_str(data):
    return f"12 kk: {data['12 kk (tod.pv/360)']} ja 3 kk: {data['3 kk (tod.pv/360)']}"


@command('euribor')
def say_euribor(bot, trigger):
    data = get_euribor_rates()
    out = euribor_data_to_str(data)
    bot.say(out)


if __name__ == '__main__':
    data = get_euribor_rates()
    print(euribor_data_to_str(data))
