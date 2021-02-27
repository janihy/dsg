# coding=utf-8
"""
    made by tuplis 2021
"""

from bs4 import BeautifulSoup

import sopel.module
import math
import requests

BASEURL = 'https://www.etaisyys.com/etaisyys'


@sopel.module.rule(r'^.matka (\w+) (\w+)(?: (\d+))?')
@sopel.module.example('!matka Helsinki Riihimäki 100')
def module(bot, trigger):
    start = trigger.group(1)
    end = trigger.group(2)
    speed = float(trigger.group(3) or 80)

    if not start or not end:
        bot.reply('!matka lähde kohde')

    try:
        response = requests.get(f"{BASEURL}/{start}/{end}", verify=False)
        dom = BeautifulSoup(response.text, 'html.parser')
        map = int(dom.find(id='totaldistancekm').get('value'), 10)
        road = int(dom.find(id='distance').get('value'), 10)

        if map == 0 or road == 0:
            bot.reply('Meiltä on nyt valitettavasti matkat päässeet loppumaan')
            return

        time = road / speed
        hours = math.floor(time)
        minutes = math.floor((time - hours) * 60)
        bot.reply(f'{start.title()} - {end.title()}: {map} km linnuntietä, {road} km tietä pitkin ({hours} h {minutes} min nopeudella {speed:.0f} km/h)')
    except Exception as e:
        bot.reply('Eipä ollu, varmaan kirjotit jotain väärin')
        bot.reply(f'{e}')
