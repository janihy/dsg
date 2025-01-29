# coding=utf-8
"""
    made by tuplis 2021-2022
"""

from sopel import plugin, db
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

import pytz
import requests
import locale
import json

locale.setlocale(locale.LC_NUMERIC, "fi_FI.UTF-8")

FMI_URL = "https://opendata.fmi.fi/wfs?service=WFS&version=2.0.0&request=getFeature&storedquery_id={query_id}&place={place}&timezone=Europe/Helsinki&starttime={starttime}&endtime={endtime}"

# https://www.ilmatieteenlaitos.fi/latauspalvelun-pikaohje
WEATHERSYMBOL3_MAP = {
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
    3: "pilvistä",
    -1: "palvelussa häire"
}

# https://www.ilmatieteenlaitos.fi/latauspalvelun-pikaohje
WW_MAP = {
    0: "ei merkittäviä sääilmiöitä (minkään alla olevan wawa-koodin ehdot eivät täyty)",
    4: "auerta, savua tai ilmassa leijuvaa pölyä ja näkyvyys vähintään 1 km",
    5: "auerta, savua tai ilmassa leijuvaa pölyä ja näkyvyys alle 1 km",
    10: "utua",
    20: "sumua",
    21: "sadetta (olomuoto on määrittelemätön)",
    22: "tihkusadetta (ei jäätävää) tai lumijyväsiä",
    23: "vesisadetta (ei jäätävää)",
    24: "lumisadetta",
    25: "jäätävää vesisadetta tai jäätävää tihkua",
    30: "sumua",
    31: "sumua tai jääsumua erillisinä hattaroina",
    32: "sumua tai jääsumua, joka on ohentunut edellisen tunnin aikana",
    33: "sumua tai jääsumua, jonka tiheydessä ei ole tapahtunut merkittäviä muutoksia edellisen tunnin aikana",
    34: "sumua tai jääsumua, joka on muodostunut tai tullut sakeammaksi edellisen tunnin aikana",
    40: "sadetta",
    41: "heikkoa tai kohtalaista sadetta (olomuoto on määrittelemätön)",
    42: "kovaa sadetta (olomuoto on määrittelemätön)",
    50: "tihkusadetta (heikkoa, ei jäätävää)",
    51: "heikkoa tihkua, joka ei ole jäätävää",
    52: "kohtalaista tihkua, joka ei ole jäätävää",
    53: "kovaa tihkua, joka ei ole jäätävää",
    54: "jäätävää heikkoa tihkua",
    55: "jäätävää kohtalaista tihkua",
    56: "jäätävää kovaa tihkua",
    60: "vesisadetta (heikkoa, ei jäätävää)",
    61: "heikkoa vesisadetta, joka ei ole jäätävää",
    62: "kohtalaista vesisadetta, joka ei ole jäätävää",
    63: "kovaa vesisadetta, joka ei ole jäätävää",
    64: "jäätävää heikkoa vesisadetta",
    65: "jäätävää kohtalaista vesisadetta",
    66: "jäätävää kovaa vesisadetta",
    67: "heikkoa lumensekaista vesisadetta tai tihkua (räntää)",
    68: "kohtalaista tai kovaa lumensekaista vesisadetta tai tihkua (räntää)",
    70: "lumisadetta",
    71: "heikkoa lumisadetta",
    72: "kohtalaista lumisadetta",
    73: "tiheää lumisadetta",
    74: "heikkoa jääjyvässadetta",
    75: "kohtalaista jääjyväsadetta",
    76: "kovaa jääjyväsadetta",
    77: "lumijyväsiä",
    78: "jääkiteitä",
    80: "kuuroja tai ajoittaista sadetta(heikkoja)",
    81: "heikkoja vesikuuroja",
    82: "kohtalaisia vesikuuroja",
    83: "kovia vesikuuroja",
    84: "ankaria vesikuuroja (>32 mm/h)",
    85: "heikkoja lumikuuroja",
    86: "kohtalaisia lumikuuroja",
    87: "kovia lumikuuroja",
    89: "raekuuroja mahdollisesti yhdessä vesi- tai räntäsateen kanssa",
    -1: "palvelussa häire"
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


def convert_float(input):
    if input == "NaN":
        return -1
    try:
        output = float(input)
    except Exception:
        return -1

    return output


def get_fmi_data(place: str) -> dict:
    # https://en.ilmatieteenlaitos.fi/open-data-manual-fmi-wfs-services

    # Real time weather observations from weather stations. Default set contains
    # air temperatire, wind speed, gust speed, wind direction, relative
    # humidity, dew point, one hour precipitation amount, precipitation
    # intensity, snow depth, pressure reduced to sea level and visibility. By
    # default, the data is returned from last 12 hour. At least one location
    # parameter (geoid/place/fmisid/wmo/bbox) has to be given. The data is
    # returned as a time value pair format.
    observations_query = "fmi::observations::weather::timevaluepair"

    # edited forecasts are curated by people inside FMI
    # Edited Scandinavia point weather forecast fetched to a specific location
    # returned in time value pair format. Location need to be specified as place
    # or geoid or latlon query parameters.
    forecast_query = "fmi::forecast::edited::weather::scandinavia::point::timevaluepair"

    starttime = (datetime.now() - timedelta(hours=1)).astimezone(pytz.utc).isoformat(timespec='seconds').replace("+00:00", "Z")
    endtime = datetime.now().astimezone(pytz.utc).isoformat(timespec='seconds').replace("+00:00", "Z")
    result = {}
    forecast = {}

    res = requests.get(FMI_URL.format(query_id=observations_query, place=place, starttime=starttime, endtime=endtime), timeout=5)
    try:
        res.raise_for_status()
        observations_soup = BeautifulSoup(res.text, features='lxml')
        result['timestamp'] = datetime.fromisoformat(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-t2m'}).find_all('wml2:time')[-1].text)
        result['place'] = observations_soup.find('gml:name').text

        observations_map = {
            "temperature": "obs-obs-1-1-t2m",
            "winddirection": "obs-obs-1-1-wd_10min",
            "windspeed": "obs-obs-1-1-ws_10min",
            "rh": "obs-obs-1-1-rh",
            "visibility": "obs-obs-1-1-vis",
            "clouds": "obs-obs-1-1-n_man",
            "rainfall": "obs-obs-1-1-r_1h",
            "snow": "obs-obs-1-1-snow_aws",
            "weather": "obs-obs-1-1-wawa"
        }
        result |= {k: convert_float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': v}).find_all('wml2:value')[-1].text) for k, v in observations_map.items()}
        result['weather'] = int(result['weather'])
    except Exception as e:
        print(e)
        return None

    try:
        timestamp = (datetime.now() + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0)
        timestamp = timestamp.isoformat().replace("+00:00", "Z")
        res = requests.get(FMI_URL.format(query_id=forecast_query, place=place, starttime=timestamp, endtime=timestamp), timeout=5)
        res.raise_for_status()

        forecast_soup = BeautifulSoup(res.text, features='lxml')
        forecast_map = {
            "temp": "mts-1-1-Temperature",
            "windspeed": "mts-1-1-WindSpeedMS",
            "weather": "mts-1-1-WeatherSymbol3"
        }
        result['forecast'] = {k: convert_float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': v}).find('wml2:value').text) for k, v in forecast_map.items()}
        result['forecast']['weather'] = int(result['forecast']['weather'])
    except Exception as e:
        result['error'] = repr(e)
    return result


@plugin.commands('sää', 'saa', 'keli')
@plugin.example(
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
    if weather is None:
        bot.say("Paikkaa ei löydy tai jotain t: fmi")
        return

    weather['temperature'] = round(weather['temperature'], 2)
    weather['timestamp'] = weather['timestamp'].strftime('%H:%M')
    weather['winddirection'] = round(weather['winddirection'])
    weather['visibility'] = round(weather['visibility'] / 1000)
    weather['weather'] = WW_MAP[round(weather['weather'])]
    try:
        weather['windfrom'] = DIRECTION_MAP[int((weather['winddirection'] + 22.5) / 45) % 8]
    except Exception:
        weather['windfrom'] = ""

    msg = "{place} {temperature:n}°C ({timestamp}), {weather}. Ilmankosteus {rh:n} %, sademäärä (<1h): {rainfall} mm.".format(**weather)
    if "windspeed" in weather and weather['windspeed'] > -1:
        msg += " Tuulee {windspeed:n} m/s {windfrom} ({winddirection:n}°).".format(**weather)
    else:
        msg += " Asemalta puuttuu tuuli."
    if "visibility" in weather and weather['visibility'] > 0:
        msg += " Näkyvyys {visibility} km".format(**weather)
    else:
        msg += " Asemalta puuttuu näkyvyys"
    if "clouds" in weather and weather['clouds'] >= 0:
        msg += ", pilvisyys {clouds:.0n}/8.".format(**weather)
    else:
        msg += " ja pilvisyyttä ei mitata."
    if "snow" in weather and weather['snow'] < 0:
        msg += " Ei lunta."
    else:
        msg += " Lumensyvyys {snow:.0f} cm.".format(**weather)
    forecast = weather['forecast']
    if "temp" in forecast:
        forecast['weather'] = WEATHERSYMBOL3_MAP[forecast['weather']]
        forecast['temp'] = round(forecast['temp'])
        forecast['windspeed'] = round(forecast['windspeed'])
        msg += " Huomispäiväksi luvattu {temp:n}°C, tuulee {windspeed:n} m/s - {weather}.".format(**forecast)

    if "error" in weather:
        msg += f" Ei kaikkia tietoja, koska {weather['error']}"
    bot.say(msg)


if __name__ == "__main__":
    print(json.dumps(get_fmi_data("Espoo"), indent=2, default=str))
