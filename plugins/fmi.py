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

locale.setlocale(locale.LC_NUMERIC, "fi_FI.UTF-8")

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
    3: "pilvistä",
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

    # The stored query can be used to fetch Harmonie surface level weather
    # forecast in time value pair format. The model data covers the
    # geographical area of Scandinavia. New forecast dataset will come
    # available every 6 hours. Location need to be specified as place or geoid
    # or latlon query parameters.
    forecast_query = "fmi::forecast::harmonie::surface::point::timevaluepair"

    # starttime = (datetime.now(timezone.utc).replace(microsecond=0) - timedelta(hours=4)).isoformat()

    # starttime = starttime.replace("+00:00", "Z")
    starttime = int((datetime.now() - timedelta(hours=1)).timestamp())
    result = {}
    result['forecast'] = {}

    res = requests.get(FMI_URL.format(query_id=observations_query, place=place, starttime=starttime), timeout=5)
    try:
        res.raise_for_status()
        observations_soup = BeautifulSoup(res.text, features='lxml')
        result['timestamp'] = datetime.fromisoformat(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-t2m'}).find_all('wml2:time')[-1].text)
        result['place'] = observations_soup.find('gml:name').text
        result['temperature'] = convert_float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-t2m'}).find_all('wml2:value')[-1].text)
        result['winddirection'] = observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-wd_10min'}).find_all('wml2:value')[-1].text
        result['winddirection'] = convert_float(result['winddirection'])
        result['windspeed'] = convert_float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-ws_10min'}).find_all('wml2:value')[-1].text)
        result['rh'] = convert_float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-rh'}).find_all('wml2:value')[-1].text)
        result['visibility'] = observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-vis'}).find_all('wml2:value')[-1].text
        result['visibility'] = convert_float(result['visibility'])
        result['clouds'] = observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-n_man'}).find_all('wml2:value')[-1].text
        result['clouds'] = convert_float(result['clouds'])
        result['rainfall'] = convert_float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-r_1h'}).find_all('wml2:value')[-1].text)
        result['snow'] = convert_float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-snow_aws'}).find_all('wml2:value')[-1].text)
        result['weather'] = round(convert_float(observations_soup.find('wml2:measurementtimeseries', {'gml:id': 'obs-obs-1-1-wawa'}).find_all('wml2:value')[-1].text))
    except Exception as e:
        print(e)
        return None

    try:
        res = requests.get(FMI_URL.format(query_id=forecast_query, place=place, starttime=starttime), timeout=5)
        res.raise_for_status()
        forecast_soup = BeautifulSoup(res.text, features='lxml')
        # RIP WeatherSymbol3, does not exist in the harmonie forecast. Old Hirlam forecast was deprecated in 10/2022.
        # result['weather'] = int(float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': 'mts-1-1-WeatherSymbol3'}).find_all('wml2:value')[0].text)) if not "NaN" else -1
        # force it to -1 until we fix it
        timestamp = (result['timestamp'] + timedelta(days=1)).replace(hour=15, minute=0, second=0, microsecond=0).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        result['forecast']['temp'] = float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': 'mts-1-1-Temperature'}).find('wml2:time', string=timestamp).find_next_sibling('wml2:value').text)
        result['forecast']['windspeed'] = float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': 'mts-1-1-WindSpeedMS'}).find_all('wml2:value')[-1].text)
        result['forecast']['cloudcoverage'] = float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': 'mts-1-1-TotalCloudCover'}).find_all('wml2:value')[-1].text)
        # result['forecastweather'] = int(float(forecast_soup.find('wml2:measurementtimeseries', {'gml:id': 'mts-1-1-WeatherSymbol3'}).find('wml2:time', string=timestamp).find_next_sibling('wml2:value').text)) if not "NaN" else -1
    except Exception as e:
        result['error'] = e
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
    weather['weather'] = round(weather['weather'])
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
        # weather['forecastweather'] = WEATHERCODE_MAP[weather['forecastweather']]
        forecast['temp'] = round(forecast['temp'])
        forecast['windspeed'] = round(forecast['windspeed'])
        msg += " Huomispäiväksi luvattu {temp:n}°C, tuulee {windspeed:n} m/s.".format(**forecast)
        if forecast['cloudcoverage'] > 80:
            msg += " Pilvistä."

    if "error" in weather:
        msg += f" Ei kaikkia tietoja, koska {weather['error']}"
    bot.say(msg)


if __name__ == "__main__":
    print(get_fmi_data("Espoo"))
