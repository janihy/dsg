# coding=utf-8
"""
    made by tuplis 2021
"""
from __future__ import (unicode_literals, absolute_import, division, print_function)

from sopel import db
from sopel.module import commands, require_privmsg, rule
from sopel.config.types import StaticSection, ValidatedAttribute

import requests

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


@commands('snp')
def fm(bot, trigger):
    last_track = {}
    action = get_action(last_track)

    # out = format_song_output(trigger.nick, action, last_track['artist']['#text'], last_track['name'], last_track['album']['#text'])

    bot.say("spotify np triggered")


@require_privmsg()
@rule(r'^.spotify auth (\w+)')
def spotify_authenticate(bot, trigger):
    authkey = trigger.group(1)

    state = db.SopelDB(bot.config)
    state.set_nick_value(trigger.nick, 'spotify_auth_key', authkey)

    bot.reply('Spotify authentication key saved.')
