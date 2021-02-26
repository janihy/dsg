# coding=utf-8
"""
    made by tuplis 2021
"""
from __future__ import (unicode_literals, absolute_import, division, print_function)

from sopel import db
from sopel.module import commands, require_privmsg, rule
from sopel.config.types import StaticSection, ValidatedAttribute

import requests
import json

SPOTIFY_AUTH_ENDPOINT = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_ENDPOINT = "https://accounts.spotify.com/api/token"


class SpotifySection(StaticSection):
    api = ValidatedAttribute('api')


def setup(bot):
    bot.config.define_section('spotify', SpotifySection)


def configure(config):
    config.define_section('spotify', SpotifySection, validate=False)
    config.spotify.configure_setting('client_id', 'Enter Spotify client ID: ')
    config.spotify.configure_setting('client_secret', 'Enter Spotify client secret: ')


class NoUserSetException(Exception):
    pass


class NoUserException(Exception):
    pass


class NoTracksException(Exception):
    pass


def format_song_output(user, action, artist, song, album):
    return f'♫ {user} {action} {artist} - {song} ♫'


def get_action(last_track):
    if last_track:
        return 'is listening to'
    else:
        return 'last listened to'


def get_now_playing(spotify):
    return "Rick Astley - Never Gonna Give You Up"


@commands('sdebug')
def spotify_debug(bot, trigger):
    state = db.SopelDB(bot.config)
    spotify = state.get_nick_value(trigger.nick, 'spotify')
    bot.reply(json.dumps(spotify))


@commands('snp')
def spotify_np(bot, trigger):

    state = db.SopelDB(bot.config)
    spotify = state.get_nick_value(trigger.nick, 'spotify')
    if not spotify:
        bot.reply('Laitoin sulle msg.')
        bot.say('spotify piste com', trigger.nick)

    # out = format_song_output(trigger.nick, action, last_track['artist']['#text'], last_track['name'], last_track['album']['#text'])


@require_privmsg()
@rule(r'^.spotify auth (\w+)')
def spotify_authenticate(bot, trigger):
    authcode = trigger.group(1)

    headers = {
        'Authorization': authcode
    }
    payload = {
        'grant_type': 'authorization_code',
        'code': authcode
    }

    res = requests.post(SPOTIFY_AUTH_ENDPOINT, headers=headers, data=payload)
    bot.reply(res.text)

    state = db.SopelDB(bot.config)

    spotify = {
        'access_token': '',
        'expires_at': '',
        'refresh_token': ''
    }
    state.set_nick_value(trigger.nick, 'spotify', spotify)

    # ask spotify api for the access_token and the refresh_token, no need to really save the auth code
    # that code will be expired quickly anyway

    bot.reply('Spotify authentication key saved.')
