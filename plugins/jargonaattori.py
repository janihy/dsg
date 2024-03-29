# coding=utf-8
"""
    made by tuplis 2021
    thank you http://jargonaattori.fi/
"""

from sopel.plugin import rule
from sopel.tools import Identifier
import random


def generate_title() -> str:
    adjectives = [
        '',
        'Executive',
        'Born-Digital',
        'Lead',
        'Enthusiaistic',
        'Digital',
        'Digital Native',
        'User',
        'Future-Proofed',
        'Humanizing',
        'Linking',
        'Challenging',
        'Podcasting',
        'Senior',
        'Public',
        'Exponential',
        'Quantitative',
        'New Commerce',
        'Agile',
        'Scrum',
        'Intelligent',
        'Penetrative',
        'Social Selling',
        'Lean',
        'Omni',
        'Native',
        'Top 30',
        'LinkedIn top 1%',
        'Social Media',
        'Pan-Disciplinary',
        'Triple Bottom Line',
        'Win-Win',
        'Human-Centric',
        'New Business',
        'Human-to-Human',
        'Platformization',
        'Physical',
        'Digital-to-analogue',
        'Value',
        'Iterative',
        'Post-Visual',
        'Client',
        'Insight',
        'Meso-level',
        'Experience',
        'Tactile',
        'Foresight',
        'Service Path',
        '360-degree',
        'Deep Learning',
        '24/7',
        'Big Data',
        'Creative',
        'Data-driven',
        'Full Stack',
        'Debundling',
        'Executive Client Account',
        'Integrated',
        'Founder &',
        '22nd Century',
        'Independent',
        'Goal-Driven',
        'Sales',
        'Networking',
        'Vice',
        'Portfolio',
        'ROI',
        'Growth',
        'Nomad',
        'Tribal',
        'UX',
        'CX',
        'Reinventing',
        'Machine-to-Human',
        'Human-to-Machine',
        'Macro-Level',
        'Anthropology',
        'Over +10k',
        'Major',
        'Platinum-Level',
        'Solutions-driven',
        'Cloud Blockchain',
        'Key Account',
        'Results-Oriented',
        'Multidisciplinary',
        'Results-Driven',
        'Funnivation',
        'Venture',
        'Silo-busting',
        'Elite',
        'Smart',
        'Visual',
        'The',
        'Award Winning',
        'Supra-Guthenbergian',
        'UX / CX / EX / xX / TedX',
        'Content',
        'Holistic',
        'Top Talent',
        'Synergizing',
        'Multi-Faceted',
        'Finding my inner',
        'Automation',
        'Emotional',
        'Engaging',
        'Insight & Research',
        'Serial',
        'Systemic',
        'Pipeline',
        'Gamified',
        'Robust',
        'Revolutionary',
        'Disruptive',
        'Passionate',
        'Extensive',
        'Cultural',
        'Frugal',
        'Ecosystem',
        'Platform',
        'Data Science',
        'Culture',
        'Empowering',
        'Enabling',
        'Sales',
        'Success',
        'Winning',
        'Chief',
        'Winning Strategies',
        'Change',
        'Megatrends',
        'Leading',
        'Culture'
    ]

    nouns = [
        'Digitalist',
        'Evangelist',
        'Preacher',
        'Designer',
        'Director',
        'Executive',
        'Service Designer',
        'Enthusiaist',
        'Lover',
        'Methuselah',
        'Manager',
        'Sculptor',
        'Speaker',
        'at the innovation industry leader',
        'Writer',
        'Naturalist',
        'Parent',
        'Professional',
        'is my passion',
        'Closer',
        'Leader',
        'at Heart',
        'Mindset',
        'Emoting',
        'Enterpreneur',
        'Problem-Solver',
        'Architect',
        'Interacting',
        'Inspirationist',
        'Poblem-Solving',
        'Master',
        'Connections',
        'Intrepreneur',
        'Guru',
        'Change Agent',
        'Sherpa',
        'Paradigm Shifting',
        'On The Go',
        'Alchemist',
        'Shaman',
        'Tactician',
        'Lifetime Learner',
        'Success',
        'Top Team',
        'Community',
        'Challenges',
        'Social Selling Influencer',
        'Representative',
        'Keynote',
        'Sprinkler',
        'Conoisseur',
        'Visualist',
        'Eye-Openings',
        'Overlord',
        'Dynamo',
        'Rock Star',
        'Jesus',
        'for Emerging Media',
        'Champion',
        'Expert Helping Companies Grow',
        'Client Executive Lead Associate Director',
        'At-Large',
        'Nostradamus',
        'Specialist',
        'Focus',
        'Angel',
        'First',
        'Technologies',
        'Contrarian',
        'MBA',
        'Team Lead',
        'Growth Hacking',
        'Harmonizer',
        'Technologist',
        'in Digitalisation',
        'with a business mindset',
        'as a Service',
        'Method',
        'Outlier',
        'Nomad',
        'Pivotization',
        'Whisperer',
        'Thought Leader',
        'Engagement',
        'Management',
        'Marketing',
        'Solutions',
        'Rouge',
        'Tip of the Spear',
        'Trainer',
        'Mentor',
        'Pro',
        'Futures',
        'Dialogues',
        'Coach',
        'Learning',
        'Futurist',
        'Intelligence',
        'Marketer',
        'Outside the Box',
        'Adventurer',
        'Design',
        'Service Design',
        'Ways for Growth',
        'Automation',
        'Visionary',
        'Analyst',
        'Co-Creation',
        'Facilitator',
        'Catalyst',
        'Interactions',
        'Raconteur',
        'Ninja',
        'Wizard',
        'Science',
        'Creator',
        'Perfectionist',
        'Agent',
        'Transformation',
        'Key User',
        'Reimagining',
        'Value Creation'
    ]

    return f"{random.choice(adjectives)} {random.choice(nouns)}"


def jargonoi_titteli() -> str:
    THRESHOLD = 0.9

    if (random.random() > THRESHOLD):
        return "Looking for new opportunities"

    titles_count = random.choice(range(1, 6))
    titles = [generate_title() for i in range(1, titles_count)]
    return ' | '. join(titles)


def jargonoi_kommentti(names: list) -> str:
    comments = [
        'Hyvin sanottu',
        'Täysin totta',
        'Itse olen tehnyt näin jo pitkään - toimii,',
        'Tästä olen puhunut paljon, tärkeä aihe',
        'Minulla oli samanlainen kokemus juuri,',
        'Nostat esille rohkeasti tärkeän aiheen,',
        'Hyvä',
        'Mahtavaa',
        '#tärkeää',
        'Huikeaa',
        '#huikea',
        'Meillä tämä näkyy päivittäin töissä,',
        'Ymmärtäsivätpä kaikki tämän,',
        'Ajankohtainen esimerkki asiasta, jota mietin paljon,',
        'Hyvin haastettu',
        'Tunnistan tarinasta itseni,',
        'Kaikkien pitäisi nehdä näin, minä teen jo näin,',
        'Juuri näin',
        'Samaa mieltä',
        'Hyödyllinen postaus',
        'Aamun paras',
        'Nyt on asiaa',
        'Sytyin',
        'Siis vau',
        'Loistavaa',
        'Näinhän se on,',
        'Sä ymmärrät tätä',
        'Pakko kommentoida,',
        'Minä voisin tässä auttaa,',
        'Tiedän tästä paljon,',
        'Tämä on tuttua,',
        'Olen kokeillut tätä usein käytännössä,',
        'Itse olen usein samassa tilanteessa tehnyt juuri noin,',
        'Tätä ei kaikki ymmärrä,',
        'Mukana,',
        'Nostaisin tähän myös asenteen tärkeäksi osaksi,',
        'Suosittelen lukemaan tämän kirjoituksen! Hyvä',
        'Hyvää keskustelua, tärkeä avaus',
        'Tätä jään seuraamaan mielenkiinnolla,',
        '💪',
        '👍',
        '💥',
        '🔥'
    ]
    # names = [
    #     'Timo',
    #     'Juha',
    #     'Matti',
    #     'Kari',
    #     'Mikko',
    #     'Antti',
    #     'Jari',
    #     'Jukka',
    #     'Markku',
    #     'Mika',
    #     'Pekka',
    #     'Hannu',
    #     'Heikki',
    #     'Seppo',
    #     'Janne',
    #     'Ari',
    #     'Sami',
    #     'Ville',
    #     'Marko',
    #     'Petri',
    #     'Lauri',
    #     'Erkki',
    #     'Jani',
    #     'Pentti',
    #     'Jorma',
    #     'Teemu',
    #     'Harri',
    #     'Eero',
    #     'Raimo',
    #     'Jaakko',
    #     'Jarmo',
    #     'Risto',
    #     'Jussi',
    #     'Pasi',
    #     'Esa',
    #     'Pertti',
    #     'Juho',
    #     'Martti',
    #     'Jouni',
    #     'Niko',
    #     'Toni',
    #     'Reijo',
    #     'Arto',
    #     'Veikko',
    #     'Markus',
    #     'Jouko',
    #     'Vesa',
    #     'Tomi',
    #     'Tuomas',
    #     'Olli',
    #     'Esko',
    #     'Aleksi',
    #     'Kimmo',
    #     'Joni',
    #     'Tommi',
    #     'Tero',
    #     'Joonas',
    #     'Henri',
    #     'Eetu',
    #     'Kalle',
    #     'Ilkka',
    #     'Leo',
    #     'Paavo',
    #     'Jarkko',
    #     'Pauli',
    #     'Jesse',
    #     'Eino',
    #     'Tuomo',
    #     'Joona',
    #     'Tapio',
    #     'Jere',
    #     'Maria',
    #     'Helena',
    #     'Anneli',
    #     'Johanna',
    #     'Kaarina',
    #     'Marjatta',
    #     'Hannele',
    #     'Kristiina',
    #     'Liisa',
    #     'Emilia',
    #     'Elina',
    #     'Tuulikki',
    #     'Annikki',
    #     'Maarit',
    #     'Sofia',
    #     'Susanna',
    #     'Leena',
    #     'Katariina',
    #     'Anna',
    #     'Marja',
    #     'Sinikka',
    #     'Inkeri',
    #     'Riitta',
    #     'Kyllikki',
    #     'Aino',
    #     'Tuula',
    #     'Anne',
    #     'Päivi',
    #     'Orvokki',
    #     'Ritva',
    #     'Tellervo',
    #     'Maija',
    #     'Pirjo',
    #     'Karoliina',
    #     'Pauliina',
    #     'Minna',
    #     'Sari',
    #     'Irmeli',
    #     'Eeva',
    #     'Tiina',
    #     'Laura',
    #     'Eveliina',
    #     'Marika',
    #     'Elisabet',
    #     'Tarja',
    #     'Pirkko',
    #     'Satu',
    #     'Anja',
    #     'Mari',
    #     'Hanna',
    #     'Seija',
    #     'Marita',
    #     'Heidi',
    #     'Eila',
    #     'Sirpa',
    #     'Raija',
    #     'Annika',
    #     'Irene',
    #     'Jaana',
    #     'Sisko',
    #     'Anita',
    #     'Sanna',
    #     'Eija',
    #     'Ilona',
    #     'Kirsi',
    #     'Marianne',
    #     'Julia',
    #     'Merja',
    #     'Amanda',
    #     'Katriina',
    #     'Ulla',
    # ]

    # TODO: add names from active irc users on the channel (like last three speakers not including the caller)

    return f"{random.choice(comments)} {random.choice(names)}!"


@rule(r'.jargonoi(?: (titteli|kommentti|users))?')
def jargonoi(bot, trigger) -> None:
    mode = trigger.group(1) or 'kommentti'
    names = [user for user in bot.users if user != bot.nick]
    if mode == "kommentti":
        bot.say(jargonoi_kommentti(names))
    if mode == "titteli":
        bot.say(jargonoi_titteli())
    elif mode == "users":
        names = [str(user) for user in bot.users if not bot.users.get(Identifier(str(user))).away and user != bot.nick]
        # bot.say(' '.join(names))
