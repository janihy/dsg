from os import getenv
import pytest
import pytest_responses

from sopel.tests import rawlist
from .euribor import *
TEST_NAME = 'test.cfg'
TEST_CONFIG = """
[core]
owner = Tuplis
nick = dsg
extra = .
"""

TEST_EURIBOR_RATES = {
    '12 kk': '0.123',
    '3 kk': '0.456',
}

MOCK_EURIBOR_RESPONSE = """<?xml version="1.0" encoding="utf-8"?>
<Report xmlns="euribor_korot_today_xml_fi">
<matrix1_Title_Collection>
<rate name="1 vko (tod.pv/360)"><intr value="2,532" /></rate>
<rate name="1 kk (tod.pv/360)"><intr value="2,446" /></rate>
<rate name="3 kk (tod.pv/360)"><intr value="2,553" /></rate>
<rate name="3 kk (tod.pv/365)"><intr value="2,588" /></rate>
<rate name="6 kk (tod.pv/360)"><intr value="2,393" /></rate>
<rate name="12 kk (tod.pv/360)"><intr value="2,449" /></rate>
</matrix1_Title_Collection>
</Report>
"""

def test_get_euribor_rates(responses):
    responses.get(
        EURIBOR_ENDPOINT,
        body=MOCK_EURIBOR_RESPONSE,
        status=200,
    )

    rates = get_euribor_rates()
    assert rates is not None
    assert len(rates) == 6

def test_euribor_data_to_str():
    assert euribor_data_to_str(TEST_EURIBOR_RATES) == "12 kk: 0.123 ja 3 kk: 0.456"

def test_euribor_with_margin_to_str():
    data = TEST_EURIBOR_RATES | {'margin': 0.5}
    assert euribor_data_to_str(data) == "12 kk: 0.123 ja 3 kk: 0.456, mutta sulle 0.623 ja 0.956"

def test_euribor_command(configfactory, botfactory, ircfactory, userfactory, responses):
    settings = configfactory(TEST_NAME, TEST_CONFIG)
    bot = botfactory.preloaded(settings, ['euribor'])
    irc = ircfactory(bot)
    user = userfactory('Tuplis')

    responses.get(
        EURIBOR_ENDPOINT,
        body=MOCK_EURIBOR_RESPONSE,
        status=200,
    )

    irc.say(user, '#test', '.euribor')

    assert bot.backend.message_sent == rawlist(
        'PRIVMSG #test :12 kk: 2,449 ja 3 kk: 2,553'
    )
