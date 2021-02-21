# coding=utf-8
"""
    made by tuplis 2021
"""
from __future__ import (unicode_literals, absolute_import, division, print_function)

import sopel.module
from sopel.config.types import StaticSection, ValidatedAttribute
import sopel.db
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


def get_api_url(user):
    return (f'http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={user}&api_key={api_key}&format=json&limit=1')


def get_action(last_track):
    if last_track:
        return 'is listening to'
    else:
        return 'last listened to'


def get_lastfm_user(arg, nick, config):
    if arg:
        return arg

    db = sopel.db.SopelDB(config)
    lastfm_user = db.get_nick_value(nick, 'lastfm_user')
    if lastfm_user:
        return lastfm_user

    msg = 'User not set, use !fmset or pass user as argument'
    raise NoUserSetException(msg)


def get_last_track(json):
    try:
        return json['recenttracks']['track'][0]
    except KeyError:
        raise NoUserException('User not found')
    except IndexError:
        raise NoTracksException('User has not listened to any tracks yet')


@sopel.module.commands('spotify')
def fm(bot, trigger):
    try:
        user = get_lastfm_user(trigger.group(2), trigger.nick, bot.config)
    except NoUserSetException as e:
        bot.say(str(e))
        return

    api_url = get_api_url(user)
    r = requests.get(api_url)

    try:
        last_track = get_last_track(r.json())
    except (NoUserException, NoTracksException) as e:
        bot.say(str(e))
        return

    action = get_action(last_track)

    out = format_song_output(user, action, last_track['artist']['#text'], last_track['name'], last_track['album']['#text'])

    bot.say(out)


@sopel.module.commands('fmset')
def fmset(bot, trigger):
    user = trigger.group(2)

    if not user:
        bot.say('no user given')
        return

    db = sopel.db.SopelDB(bot.config)
    db.set_nick_value(trigger.nick, 'lastfm_user', user)

    bot.say(f'{trigger.nick}\'s last.fm user is now set as {user}')
