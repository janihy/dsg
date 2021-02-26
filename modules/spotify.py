# coding=utf-8
"""
    made by tuplis 2021
"""
from __future__ import (unicode_literals, absolute_import, division, print_function)

from sopel import db
from sopel.module import commands, require_privmsg, rule
from sopel.config.types import StaticSection, ValidatedAttribute
from base64 import b64encode

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
        mode = "is listening to"
    else:
        mode = "last listened to"
    return f'♫ {user} {mode} {artist} - {title} ({uri}) ♫'


def get_now_playing(spotify):
    headers = {
        'Authorization': f'Bearer {spotify.get("access_token")}'
    }
    res = requests.get(SPOTIFY_NP_ENDPOINT, headers=headers)
    item = res.json().get('item')

    np = {
        'artist': item.get('artists', [{}])[0].get('name'),
        'title': item.get('name'),
        'uri': item.get('uri'),
        'currently_playing': res.json().get('is_playing')
    }

    return np


@require_privmsg()
@rule(r'^.spotify debug')
def spotify_debug(bot, trigger):
    state = db.SopelDB(bot.config)
    spotify = state.get_nick_value(trigger.nick, 'spotify')
    bot.reply(json.dumps(spotify))


@commands('snp')
def spotify_np(bot, trigger):
    client_id = bot.config.spotify.client_id
    state = db.SopelDB(bot.config)
    spotify = state.get_nick_value(trigger.nick, 'spotify')
    if not spotify:
        bot.reply('Laitoin sulle msg.')
        bot.say(SPOTIFY_AUTH_ENDPOINT.format(client_id=client_id), trigger.nick)
    else:
        # the user has already registered and everything should be fine
        np = get_now_playing(spotify)
        bot.say(format_song_output(trigger.nick, np))

    # out = format_song_output(trigger.nick, action, last_track['artist']['#text'], last_track['name'], last_track['album']['#text'])


@require_privmsg()
@rule(r'^.spotify auth (\S+)')
def spotify_authenticate(bot, trigger):
    authcode = trigger.group(1)
    client_id = bot.config.spotify.client_id
    client_secret = bot.config.spotify.client_secret
    state = db.SopelDB(bot.config)

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
        response = json.loads(res.text)

        spotify = {
            'access_token': response.get('access_token'),
            'expires_at': '',
            'refresh_token': response.get('refresh_token')
        }
        state.set_nick_value(trigger.nick, 'spotify', spotify)

        # ask spotify api for the access_token and the refresh_token, no need to really save the auth code
        # that code will be expired quickly anyway

        bot.reply('Spotify authentication key saved.')

    else:
        bot.reply('Spotify authentication failed :-(')
