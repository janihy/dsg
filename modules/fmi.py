# coding=utf8
"""
    made by tuplis 2021
"""
from __future__ import unicode_literals, absolute_import, division, print_function
from sopel import module, db

import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

FMI_URL = "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id={query_id}&place={place}&timezone=Europe/Helsinki&starttime={starttime}"
WEATHERCODE_MAP = {
    21: "heikkoja sadekuuroja",
    22: "sadekuuroja",
    23: "voimakkaita sadekuuroja",
    31: "heikkoa vesisadetta",
    32: "vesisadetta",
    33: "voimakasta vesisadetta",
    41: "heikkoja lumikuuroja",
    42: "lumikuuroja",
    43: "voimakkaita lumikuuroja",
    51: "heikkoa lumisadetta",
    52: "lumisadetta",
    53: "voimakasta lumisadetta",
    61: "ukkoskuuroja",
    62: "voimakkaita ukkoskuuroja",
    63: "ukkosta",
    64: "voimakasta ukkosta",
    71: "heikkoja räntäkuuroja",
    72: "räntäkuuroja",
    73: "voimakkaita räntäkuuroja",
    81: "heikkoa räntäsadetta",
    82: "räntäsadetta",
    83: "voimakasta räntäsadetta",
    91: "utua",
    92: "sumua",
    1: "selkeää",
    2: "puolipilvistä",
    3: "pilvistä"
}

DIRECTION_MAP = {
    0: "pohjoisesta",
    1: "koillisesta",
    2: "idästä",
    3: "kaakosta",
    4: "etelästä",
    5: "lounaasta",
    6: "lännestä",
    7: "luoteesta"
}


def configure(config):
    pass


def setup(bot):
    pass


def get_fmi_data(place: str) -> {}:
    observations_query = "fmi::observations::weather::timevaluepair"
    forecast_query = "fmi::forecast::hirlam::surface::point::timevaluepair"
    starttime = int((datetime.now() - timedelta(hours=1)).timestamp())
    result = {}

    res = requests.get(FMI_URL.format(query_id=observations_query, place=place, starttime=starttime))
    observations_soup = BeautifulSoup(res.text, features='lxml')
    res = requests.get(FMI_URL.format(query_id=forecast_query, place=place, starttime=starttime))
    forecast_soup = BeautifulSoup(res.text, features='lxml')
    print(forecast_soup)

    result['timestamp'] = datetime.strptime(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-t2m'}).find_all('wml2:time')[-1].text, "%Y-%m-%dT%H:%M:%S+02:00")
    result['place'] = observations_soup.find('gml:name').text
    result['temperature'] = observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-t2m'}).find_all('wml2:value')[-1].text
    result['winddirection'] = float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-wd_10min'}).find_all('wml2:value')[-1].text)
    result['windspeed'] = float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-ws_10min'}).find_all('wml2:value')[-1].text)
    result['rh'] = float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-rh'}).find_all('wml2:value')[-1].text)
    result['visibility'] = float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-vis'}).find_all('wml2:value')[-1].text)
    result['clouds'] = float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-n_man'}).find_all('wml2:value')[-1].text)
    result['weather'] = int(float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': 'mts-1-1-WeatherSymbol3'}).find_all('wml2:value')[0].text))
    result['rainfall'] = observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-r_1h'}).find_all('wml2:value')[-1].text if not "NaN" else 0
    result['snow'] = float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-snow_aws'}).find_all('wml2:value')[-1].text)

    timestamp = str((result['timestamp'] + timedelta(days=1)).strftime('%Y-%m-%dT15:00:00+02:00'))
    result['forecasttemp'] = float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': 'mts-1-1-Temperature'}).find('wml2:time', string=timestamp).find_next_sibling('wml2:value').text)
    result['forecastweather'] = int(float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': 'mts-1-1-WeatherSymbol3'}).find('wml2:time', string=timestamp).find_next_sibling('wml2:value').text))
    print(result)
    return result


@module.commands('sää')
@module.commands('saa')
@module.commands('keli')
@module.example(
    '!sää Espoo',
    'sää espoo',
    online=True)
def print_weather(bot, trigger):
    location = trigger.group(2)
    if not location:
        state = db.SopelDB(bot.config)
        fmi_last_location = state.get_nick_value(trigger.nick, 'fmi_last_location')
        if fmi_last_location:
            location = fmi_last_location
        else:
            location = "Espoo"
    else:
        state = db.SopelDB(bot.config)
        state.set_nick_value(trigger.nick, 'fmi_last_location', location)

    weather = get_fmi_data(location)
    weather['timestamp'] = weather['timestamp'].strftime('%H:%M')
    weather['winddirection'] = weather['winddirection']
    weather['visibility'] = weather['visibility'] / 1000
    weather['weather'] = WEATHERCODE_MAP[weather['weather']]
    weather['forecastweather'] = WEATHERCODE_MAP[weather['forecastweather']]
    try:
        weather['windfrom'] = DIRECTION_MAP[int((weather['winddirection'] + 22.5) / 45) % 8]
    except Exception:
        weather['windfrom'] = ""

    msg = "{place} {temperature}°C ({timestamp}), {weather}. Ilmankosteus {rh:.0f} %, sademäärä (<1h): {rainfall} mm. Tuulee {windspeed} m/s {windfrom} ({winddirection:.0f}°). Näkyvyys {visibility:.0f} km, pilvisyys {clouds:.0f}/8. Lumensyvyys {snow:.0f} cm. Huomispäiväksi luvattu {forecasttemp:.1f}°C, {forecastweather}.".format(**weather)
    bot.say(msg)


if __name__ == "__main__":
    try:
        from sopel.test_tools import run_example_tests
        run_example_tests(__file__)
    except Exception:
        pass
