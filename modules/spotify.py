# coding=utf-8
"""
    made by tuplis 2021
"""

from sopel import db
from sopel.module import require_privmsg, rule
from sopel.config.types import StaticSection, ValidatedAttribute
from base64 import b64encode
from datetime import datetime, timedelta

import requests
import json

SPOTIFY_AUTH_ENDPOINT = "https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&scope=user-read-playback-state&redirect_uri=https%3A%2F%2Fdsg.fi%2Fbot-callback%2F"
SPOTIFY_TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"
SPOTIFY_NP_ENDPOINT = "https://api.spotify.com/v1/me/player"


class SpotifySection(StaticSection):
    client_id = ValidatedAttribute('client_id')
    client_secret = ValidatedAttribute('client_secret')


def setup(bot):
    bot.config.define_section('spotify', SpotifySection)


def configure(config):
    config.define_section('spotify', SpotifySection, validate=False)
    config.spotify.configure_setting('client_id', 'Enter Spotify client ID: ')
    config.spotify.configure_setting('client_secret', 'Enter Spotify client secret: ')


def format_song_output(user, np):
    artist = np.get('artist')
    title = np.get('title')
    uri = np.get('uri')
    if np.get('currently_playing'):
        action = "is listening to"
    else:
        action = "last listened to"
    return f'♫ {user} {action} {artist} - {title} ({uri}) ♫'


def refresh_spotify_token(bot, nick, spotify):
    client_id = bot.config.spotify.client_id
    client_secret = bot.config.spotify.client_secret
    headers = {
        'Authorization': 'Basic ' + b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')
    }
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': spotify.get('refresh_token')
    }
    response = requests.post(SPOTIFY_TOKEN_ENDPOINT, headers=headers, data=payload)

    if response.status_code == 200:
        response = response.json()
        spotify.update({
            'access_token': response.get('access_token'),
            'expires_at': (datetime.now() + timedelta(seconds=response.get('expires_in'))).isoformat()
        })

        state = db.SopelDB(bot.config)
        state.set_nick_value(nick, 'spotify', spotify)

        return spotify
    else:
        bot.say('refresh token puuttuu tai jotain :-(')


def get_now_playing(bot, nick, spotify):
    if not spotify.get('expires_at') or datetime.fromisoformat(spotify.get('expires_at')) < datetime.now():
        spotify = refresh_spotify_token(bot, nick, spotify)

    headers = {
        'Authorization': f'Bearer {spotify.get("access_token")}'
    }
    res = requests.get(SPOTIFY_NP_ENDPOINT, headers=headers).json()
    item = res.get('item')

    np = {
        'artist': item.get('artists', [{}])[0].get('name'),
        'title': item.get('name'),
        'uri': item.get('uri'),
        'currently_playing': res.get('is_playing')
    }

    return np


@require_privmsg()
@rule(r'^.spotify debug')
def spotify_debug(bot, trigger):
    state = db.SopelDB(bot.config)
    spotify = state.get_nick_value(trigger.nick, 'spotify')
    bot.reply(json.dumps(spotify))


@require_privmsg()
@rule(r'^.spotify forget')
def spotify_forget(bot, trigger):
    state = db.SopelDB(bot.config)
    state.delete_nick_value(trigger.nick, 'spotify')


@rule(r'^!np(?: (\S+))?')
def spotify_np(bot, trigger):
    client_id = bot.config.spotify.client_id
    state = db.SopelDB(bot.config)
    nick = trigger.group(1) or trigger.nick
    spotify = state.get_nick_value(nick, 'spotify')
    if not spotify:
        # user hasn't gone through the authentication flow, let's send
        # a link to the authenticator
        if nick == trigger.nick:
            bot.reply('Laitoin sulle msg.')
            bot.say(SPOTIFY_AUTH_ENDPOINT.format(client_id=client_id), nick)
        else:
            bot.say(f'{nick} on varmaan joku köyhä jolla ei oo varaa spotifyyn :/')
    else:
        # the user has already registered and everything should be fine
        np = get_now_playing(bot, nick, spotify)
        bot.say(format_song_output(nick, np))


@require_privmsg()
@rule(r'^.spotify auth (\S+)')
def spotify_authenticate(bot, trigger):
    # we'll follow the Authorization Code flow from Spotify docs:
    # https://developer.spotify.com/documentation/general/guides/authorization-guide/

    authcode = trigger.group(1)
    client_id = bot.config.spotify.client_id
    client_secret = bot.config.spotify.client_secret

    headers = {
        'Authorization': 'Basic ' + b64encode(f'{client_id}:{client_secret}'.encode('utf-8')).decode('utf-8')
    }
    payload = {
        'grant_type': 'authorization_code',
        'code': authcode,
        'redirect_uri': 'https://dsg.fi/bot-callback/'
    }
    res = requests.post(SPOTIFY_TOKEN_ENDPOINT, headers=headers, data=payload)

    if res.status_code == 200:
        state = db.SopelDB(bot.config)
        response = json.loads(res.text)

        spotify = {
            'access_token': response.get('access_token'),
            'expires_at': (datetime.now() + timedelta(seconds=response.get('expires_in'))).isoformat(),
            'refresh_token': response.get('refresh_token')
        }
        state.set_nick_value(trigger.nick, 'spotify', spotify)
        bot.say('5/5')
    else:
        bot.say('Nyt meni joku perseelleen vituiks :-(')
