# coding=utf8
"""
made by tuplis 2021-2025
"""

from sopel import plugin, tools, db
from typing import Dict, Optional
from decimal import Decimal

import requests
import json
import datetime

REKO_ENDPOINT = "https://reko.biltema.com/v1/Reko/carinfo/{licenseplate}/3/fi"
REKO2_ENDPOINT = "https://reko2.biltema.com/VehicleInformation/licensePlate/{licenseplate}"
MOTONET_ENDPOINT = "https://www.motonet.fi/api/vehicleInfo/registrationNumber/FI"
HUUTOKAUPAT_ENDPOINT = "https://huutokaupat.com/api/net-auctions/list"
NETTIX_ENDPOINT = "https://api.nettix.fi/rest/car/search"
DSG_ENDPOINT = "http://localhost:8000"
LEIMA_ENDPOINT = "https://ajanvaraus.idealinspect.fi/api/chains/107/stations/307/vehicles/search"

NEDC_MAP = {
    0: 106.21,
    1: 106.21,
    2: 106.21,
    3: 106.21,
    4: 106.21,
    5: 106.21,
    6: 106.21,
    7: 106.21,
    8: 106.21,
    9: 106.21,
    10: 106.21,
    11: 106.21,
    12: 106.21,
    13: 106.21,
    14: 106.21,
    15: 106.21,
    16: 106.21,
    17: 106.21,
    18: 106.21,
    19: 106.21,
    20: 106.21,
    21: 106.21,
    22: 106.21,
    23: 106.21,
    24: 106.21,
    25: 106.21,
    26: 106.21,
    27: 106.21,
    28: 106.21,
    29: 106.21,
    30: 106.21,
    31: 106.21,
    32: 106.21,
    33: 106.21,
    34: 106.21,
    35: 106.21,
    36: 106.21,
    37: 106.21,
    38: 106.21,
    39: 106.21,
    40: 106.21,
    41: 106.21,
    42: 106.21,
    43: 106.21,
    44: 106.21,
    45: 106.21,
    46: 106.21,
    47: 106.21,
    48: 106.21,
    49: 106.21,
    50: 106.21,
    51: 106.21,
    52: 106.21,
    53: 106.21,
    54: 106.21,
    55: 106.21,
    56: 106.21,
    57: 106.21,
    58: 106.21,
    59: 106.21,
    60: 106.21,
    61: 106.21,
    62: 106.21,
    63: 106.21,
    64: 106.21,
    65: 106.21,
    66: 106.21,
    67: 106.21,
    68: 106.21,
    69: 106.21,
    70: 106.21,
    71: 106.21,
    72: 106.21,
    73: 106.21,
    74: 106.21,
    75: 106.21,
    76: 106.21,
    77: 106.21,
    78: 106.21,
    79: 106.21,
    80: 106.21,
    81: 106.21,
    82: 106.21,
    83: 106.58,
    84: 107.67,
    85: 108.77,
    86: 109.86,
    87: 110.96,
    88: 112.05,
    89: 112.78,
    90: 113.88,
    91: 114.97,
    92: 116.07,
    93: 117.16,
    94: 118.26,
    95: 119.72,
    96: 120.81,
    97: 121.91,
    98: 123.00,
    99: 124.10,
    100: 125.56,
    101: 126.65,
    102: 127.75,
    103: 129.21,
    104: 130.30,
    105: 131.40,
    106: 132.86,
    107: 133.95,
    108: 135.41,
    109: 136.51,
    110: 137.97,
    111: 138.70,
    112: 139.79,
    113: 140.89,
    114: 141.62,
    115: 142.71,
    116: 143.81,
    117: 144.90,
    118: 145.63,
    119: 146.73,
    120: 147.82,
    121: 148.92,
    122: 149.65,
    123: 150.74,
    124: 151.84,
    125: 152.93,
    126: 153.66,
    127: 154.76,
    128: 155.85,
    129: 156.95,
    130: 157.68,
    131: 158.77,
    132: 159.87,
    133: 160.96,
    134: 161.69,
    135: 162.79,
    136: 163.88,
    137: 164.61,
    138: 165.71,
    139: 166.80,
    140: 167.90,
    141: 168.63,
    142: 169.72,
    143: 170.82,
    144: 171.91,
    145: 172.64,
    146: 173.74,
    147: 174.83,
    148: 175.93,
    149: 176.66,
    150: 177.75,
    151: 178.85,
    152: 179.94,
    153: 180.67,
    154: 181.77,
    155: 182.86,
    156: 183.96,
    157: 184.69,
    158: 185.78,
    159: 186.88,
    160: 187.61,
    161: 188.70,
    162: 189.80,
    163: 190.89,
    164: 191.62,
    165: 192.72,
    166: 193.81,
    167: 194.91,
    168: 195.64,
    169: 196.73,
    170: 197.83,
    171: 198.92,
    172: 199.65,
    173: 200.75,
    174: 201.84,
    175: 202.94,
    176: 206.59,
    177: 210.24,
    178: 214.25,
    179: 217.90,
    180: 221.92,
    181: 225.57,
    182: 229.22,
    183: 233.23,
    184: 236.88,
    185: 240.90,
    186: 244.55,
    187: 248.20,
    188: 252.21,
    189: 255.86,
    190: 259.88,
    191: 263.53,
    192: 267.18,
    193: 271.19,
    194: 274.84,
    195: 278.86,
    196: 282.51,
    197: 286.52,
    198: 290.17,
    199: 293.82,
    200: 297.84,
    201: 301.49,
    202: 305.50,
    203: 309.15,
    204: 312.80,
    205: 316.82,
    206: 320.47,
    207: 324.48,
    208: 328.13,
    209: 331.78,
    210: 335.80,
    211: 339.45,
    212: 341.27,
    213: 343.46,
    214: 345.65,
    215: 347.84,
    216: 350.03,
    217: 352.22,
    218: 354.41,
    219: 356.60,
    220: 358.79,
    221: 360.98,
    222: 363.17,
    223: 365.36,
    224: 367.55,
    225: 369.74,
    226: 371.93,
    227: 374.12,
    228: 376.31,
    229: 378.50,
    230: 380.69,
    231: 382.88,
    232: 385.07,
    233: 387.63,
    234: 389.82,
    235: 392.01,
    236: 394.20,
    237: 396.39,
    238: 398.58,
    239: 400.77,
    240: 402.96,
    241: 405.15,
    242: 407.34,
    243: 409.53,
    244: 412.08,
    245: 414.27,
    246: 416.46,
    247: 418.65,
    248: 420.84,
    249: 423.03,
    250: 425.22,
    251: 427.41,
    252: 429.60,
    253: 431.79,
    254: 433.98,
    255: 436.17,
    256: 438.36,
    257: 440.55,
    258: 442.74,
    259: 444.93,
    260: 447.12,
    261: 449.31,
    262: 451.50,
    263: 453.69,
    264: 455.88,
    265: 457.71,
    266: 459.90,
    267: 462.09,
    268: 464.28,
    269: 466.47,
    270: 468.66,
    271: 470.48,
    272: 472.67,
    273: 474.86,
    274: 477.05,
    275: 478.88,
    276: 481.07,
    277: 483.26,
    278: 485.08,
    279: 487.27,
    280: 489.10,
    281: 491.29,
    282: 493.11,
    283: 495.30,
    284: 497.49,
    285: 499.32,
    286: 501.14,
    287: 503.33,
    288: 505.16,
    289: 507.35,
    290: 509.17,
    291: 511.00,
    292: 513.19,
    293: 515.01,
    294: 516.84,
    295: 518.66,
    296: 520.49,
    297: 522.68,
    298: 524.50,
    299: 526.33,
    300: 528.15,
    301: 529.98,
    302: 531.80,
    303: 533.63,
    304: 535.45,
    305: 537.28,
    306: 539.10,
    307: 540.56,
    308: 542.39,
    309: 544.21,
    310: 546.04,
    311: 547.86,
    312: 549.32,
    313: 551.15,
    314: 552.61,
    315: 554.43,
    316: 556.26,
    317: 557.72,
    318: 559.54,
    319: 561.00,
    320: 562.83,
    321: 564.29,
    322: 565.75,
    323: 567.57,
    324: 569.03,
    325: 570.49,
    326: 571.95,
    327: 573.78,
    328: 575.24,
    329: 576.70,
    330: 578.16,
    331: 579.62,
    332: 581.08,
    333: 582.54,
    334: 584.00,
    335: 585.46,
    336: 586.92,
    337: 588.38,
    338: 589.84,
    339: 590.93,
    340: 592.39,
    341: 593.85,
    342: 595.31,
    343: 596.41,
    344: 597.87,
    345: 599.33,
    346: 600.42,
    347: 601.88,
    348: 602.98,
    349: 604.44,
    350: 605.53,
    351: 606.99,
    352: 608.09,
    353: 609.18,
    354: 610.64,
    355: 611.74,
    356: 612.83,
    357: 613.93,
    358: 615.02,
    359: 616.48,
    360: 617.58,
    361: 618.67,
    362: 619.77,
    363: 620.86,
    364: 621.96,
    365: 623.05,
    366: 624.15,
    367: 625.24,
    368: 626.34,
    369: 627.43,
    370: 628.16,
    371: 629.26,
    372: 630.35,
    373: 631.45,
    374: 632.18,
    375: 633.27,
    376: 634.37,
    377: 635.10,
    378: 636.19,
    379: 636.92,
    380: 638.02,
    381: 639.11,
    382: 639.84,
    383: 640.57,
    384: 641.67,
    385: 642.40,
    386: 643.49,
    387: 644.22,
    388: 644.95,
    389: 646.05,
    390: 646.78,
    391: 647.51,
    392: 648.24,
    393: 649.33,
    394: 650.06,
    395: 650.79,
    396: 651.52,
    397: 652.25,
    398: 652.98,
    399: 653.71,
    400: 654.44,
}

WLTP_MAP = {
    0: 106.21,
    1: 106.21,
    2: 106.21,
    3: 106.21,
    4: 106.21,
    5: 106.21,
    6: 106.21,
    7: 106.21,
    8: 106.21,
    9: 106.21,
    10: 106.21,
    11: 106.21,
    12: 106.21,
    13: 106.21,
    14: 106.21,
    15: 106.21,
    16: 106.21,
    17: 106.21,
    18: 106.21,
    19: 106.21,
    20: 106.21,
    21: 106.21,
    22: 106.21,
    23: 106.21,
    24: 106.21,
    25: 106.21,
    26: 106.21,
    27: 106.21,
    28: 106.21,
    29: 106.21,
    30: 106.21,
    31: 106.21,
    32: 106.21,
    33: 106.21,
    34: 106.21,
    35: 106.21,
    36: 106.21,
    37: 106.21,
    38: 106.21,
    39: 106.21,
    40: 106.21,
    41: 106.21,
    42: 106.21,
    43: 106.21,
    44: 106.21,
    45: 106.21,
    46: 106.21,
    47: 106.21,
    48: 106.21,
    49: 106.21,
    50: 106.21,
    51: 106.21,
    52: 106.21,
    53: 106.21,
    54: 106.21,
    55: 106.21,
    56: 106.21,
    57: 106.21,
    58: 106.21,
    59: 106.21,
    60: 106.21,
    61: 106.21,
    62: 106.21,
    63: 106.21,
    64: 106.21,
    65: 106.21,
    66: 106.21,
    67: 106.21,
    68: 106.21,
    69: 106.21,
    70: 106.21,
    71: 106.21,
    72: 106.21,
    73: 106.21,
    74: 106.21,
    75: 106.21,
    76: 106.21,
    77: 106.21,
    78: 106.21,
    79: 106.21,
    80: 106.21,
    81: 106.21,
    82: 106.21,
    83: 106.21,
    84: 106.21,
    85: 106.21,
    86: 106.21,
    87: 106.21,
    88: 106.21,
    89: 106.21,
    90: 106.21,
    91: 106.21,
    92: 106.21,
    93: 106.21,
    94: 106.21,
    95: 106.21,
    96: 106.21,
    97: 106.21,
    98: 106.21,
    99: 106.21,
    100: 106.21,
    101: 106.21,
    102: 106.21,
    103: 106.21,
    104: 106.94,
    105: 107.67,
    106: 108.40,
    107: 109.50,
    108: 110.23,
    109: 110.96,
    110: 112.05,
    111: 112.78,
    112: 113.51,
    113: 114.61,
    114: 115.34,
    115: 116.07,
    116: 117.16,
    117: 117.89,
    118: 118.99,
    119: 119.72,
    120: 120.81,
    121: 121.54,
    122: 122.64,
    123: 123.37,
    124: 124.46,
    125: 125.56,
    126: 126.29,
    127: 127.38,
    128: 128.48,
    129: 129.21,
    130: 130.30,
    131: 131.40,
    132: 132.13,
    133: 133.22,
    134: 134.32,
    135: 135.41,
    136: 136.51,
    137: 137.60,
    138: 139.43,
    139: 140.89,
    140: 142.71,
    141: 144.54,
    142: 146.36,
    143: 147.82,
    144: 149.65,
    145: 151.47,
    146: 153.30,
    147: 155.12,
    148: 156.95,
    149: 158.77,
    150: 160.96,
    151: 162.79,
    152: 164.61,
    153: 166.80,
    154: 168.63,
    155: 170.45,
    156: 172.64,
    157: 174.83,
    158: 176.66,
    159: 178.85,
    160: 181.04,
    161: 183.23,
    162: 185.42,
    163: 187.61,
    164: 189.80,
    165: 191.99,
    166: 194.18,
    167: 196.73,
    168: 198.92,
    169: 201.11,
    170: 203.67,
    171: 205.86,
    172: 208.41,
    173: 210.97,
    174: 213.16,
    175: 215.71,
    176: 218.27,
    177: 220.82,
    178: 223.38,
    179: 225.93,
    180: 228.49,
    181: 231.04,
    182: 233.96,
    183: 236.52,
    184: 239.07,
    185: 241.99,
    186: 244.55,
    187: 247.47,
    188: 250.02,
    189: 252.94,
    190: 255.86,
    191: 258.78,
    192: 261.70,
    193: 264.62,
    194: 267.54,
    195: 270.46,
    196: 273.38,
    197: 276.30,
    198: 279.22,
    199: 282.51,
    200: 285.43,
    201: 288.71,
    202: 291.63,
    203: 294.92,
    204: 297.84,
    205: 301.12,
    206: 304.41,
    207: 307.69,
    208: 310.61,
    209: 313.90,
    210: 316.45,
    211: 319.01,
    212: 321.56,
    213: 324.12,
    214: 326.67,
    215: 329.23,
    216: 332.15,
    217: 334.70,
    218: 337.26,
    219: 339.81,
    220: 342.73,
    221: 345.29,
    222: 347.84,
    223: 350.76,
    224: 353.32,
    225: 355.87,
    226: 358.79,
    227: 361.35,
    228: 364.27,
    229: 366.82,
    230: 369.74,
    231: 372.30,
    232: 374.85,
    233: 377.77,
    234: 380.33,
    235: 383.25,
    236: 386.17,
    237: 388.72,
    238: 391.64,
    239: 394.20,
    240: 397.12,
    241: 399.67,
    242: 402.59,
    243: 405.15,
    244: 408.07,
    245: 410.62,
    246: 413.54,
    247: 416.10,
    248: 419.02,
    249: 421.57,
    250: 424.49,
    251: 427.41,
    252: 429.60,
    253: 431.79,
    254: 433.98,
    255: 436.17,
    256: 438.36,
    257: 440.55,
    258: 442.74,
    259: 444.93,
    260: 447.12,
    261: 449.31,
    262: 451.50,
    263: 453.69,
    264: 455.88,
    265: 457.71,
    266: 459.90,
    267: 462.09,
    268: 464.28,
    269: 466.47,
    270: 468.66,
    271: 470.48,
    272: 472.67,
    273: 474.86,
    274: 477.05,
    275: 478.88,
    276: 481.07,
    277: 483.26,
    278: 485.08,
    279: 487.27,
    280: 489.10,
    281: 491.29,
    282: 493.11,
    283: 495.30,
    284: 497.49,
    285: 499.32,
    286: 501.14,
    287: 503.33,
    288: 505.16,
    289: 507.35,
    290: 509.17,
    291: 511.00,
    292: 513.19,
    293: 515.01,
    294: 516.84,
    295: 518.66,
    296: 520.49,
    297: 522.68,
    298: 524.50,
    299: 526.33,
    300: 528.15,
    301: 529.98,
    302: 531.80,
    303: 533.63,
    304: 535.45,
    305: 537.28,
    306: 539.10,
    307: 540.56,
    308: 542.39,
    309: 544.21,
    310: 546.04,
    311: 547.86,
    312: 549.32,
    313: 551.15,
    314: 552.61,
    315: 554.43,
    316: 556.26,
    317: 557.72,
    318: 559.54,
    319: 561.00,
    320: 562.83,
    321: 564.29,
    322: 565.75,
    323: 567.57,
    324: 569.03,
    325: 570.49,
    326: 571.95,
    327: 573.78,
    328: 575.24,
    329: 576.70,
    330: 578.16,
    331: 579.62,
    332: 581.08,
    333: 582.54,
    334: 584.00,
    335: 585.46,
    336: 586.92,
    337: 588.38,
    338: 589.84,
    339: 590.93,
    340: 592.39,
    341: 593.85,
    342: 595.31,
    343: 596.41,
    344: 597.87,
    345: 599.33,
    346: 600.42,
    347: 601.88,
    348: 602.98,
    349: 604.44,
    350: 605.53,
    351: 606.99,
    352: 608.09,
    353: 609.18,
    354: 610.64,
    355: 611.74,
    356: 612.83,
    357: 613.93,
    358: 615.02,
    359: 616.48,
    360: 617.58,
    361: 618.67,
    362: 619.77,
    363: 620.86,
    364: 621.96,
    365: 623.05,
    366: 624.15,
    367: 625.24,
    368: 626.34,
    369: 627.43,
    370: 628.16,
    371: 629.26,
    372: 630.35,
    373: 631.45,
    374: 632.18,
    375: 633.27,
    376: 634.37,
    377: 635.10,
    378: 636.19,
    379: 636.92,
    380: 638.02,
    381: 639.11,
    382: 639.84,
    383: 640.57,
    384: 641.67,
    385: 642.40,
    386: 643.49,
    387: 644.22,
    388: 644.95,
    389: 646.05,
    390: 646.78,
    391: 647.51,
    392: 648.24,
    393: 649.33,
    394: 650.06,
    395: 650.79,
    396: 651.52,
    397: 652.25,
    398: 652.98,
    399: 653.71,
    400: 654.44,
}

FUEL_TAX_MAP = {
    "diesel": 0.055,
    "sähkö": 0.019,
}

HUUTOKAUPAT_MANUFACTURER_MAP = {"vw": "volkswagen"}

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def base_tax_from_mass(mass: int) -> Optional[float]:
    start = 0.468
    if mass <= 1300:
        k = 0
    elif mass > 1300 and mass <= 3400:
        k = ((mass-1) // 100 - 12)
    else:
        k = 22
    total = start + 0.001*k**2 + 0.029*k
    return round(total * 365, 3)


def base_tax_from_co2(measurement_type: str, co2: int) -> Optional[float]:
    if co2 > 400:
        return round(1.793 * 365, 3)

    if measurement_type == "nedc":
        return NEDC_MAP[co2]
    if measurement_type == "wltp":
        return WLTP_MAP[co2]
    else:
        return None


def fuel_tax_from_mass(mass: int, fuel_type: str = "diesel") -> Optional[float]:
    # you know, float arithmetic
    kg = -(mass // -100)
    return kg * FUEL_TAX_MAP[fuel_type]


def configure(config):
    pass


def setup(bot):
    if "nettix_token" not in bot.memory:
        bot.memory["nettix_token"] = tools.SopelMemory()


def refresh_nettix_token(bot) -> bool:
    res = requests.post("https://auth.nettix.fi/oauth2/token", data={"grant_type": "client_credentials"})
    token = json.loads(res.text)
    bot.memory["nettix_token"]["access_token"] = token.get("access_token", "")
    bot.memory["nettix_token"]["expires_in"] = datetime.datetime.now() + datetime.timedelta(
        seconds=token.get("expires_in", "")
    )
    return res.status_code == 200


def get_nettix_link(bot, licenseplate) -> Optional[str]:
    if bot.memory["nettix_token"].get("expires_in", datetime.datetime.now()) <= datetime.datetime.now():
        if not refresh_nettix_token(bot):
            bot.say("oops, nettix api broken")

    headers = {
        "Accept": "application/json",
        "X-Access-Token": bot.memory["nettix_token"].get("access_token"),
    }

    payload = {"identificationList": licenseplate}

    res = requests.get(NETTIX_ENDPOINT, params=payload, headers=headers)
    nettix_ad = json.loads(res.text)
    if nettix_ad:
        return nettix_ad[0].get("adUrl")
    else:
        return None


def get_huutokaupatcom_link(manufacturer, year, licenseplate) -> Optional[str]:
    # for example https://huutokaupat.com/api/net-auctions/list?merkki=audi&sivu=1&vuosimalliMin=2022&vuosimalliMax=2022
    # huutokaupat.com public api does not allow us to search by license plate directly, so we need to get some listings and filter them

    # vw does not equal volkswagen etc
    if manufacturer.lower() in HUUTOKAUPAT_MANUFACTURER_MAP:
        manufacturer = HUUTOKAUPAT_MANUFACTURER_MAP[manufacturer.lower()]
    params = {
        "merkki": manufacturer.lower(),
        "vuosimalliMin": year - 1,
        "vuosimalliMax": year + 1,
    }
    res = requests.get(HUUTOKAUPAT_ENDPOINT, params=params).json()
    huutokaupat_entries = res.get("entries", [])
    for entry in huutokaupat_entries:
        if entry.get("metadata", {}).get("licenseNumber") == licenseplate.upper():
            return f"https://huutokaupat.com/kohde/{entry.get('id')}/{entry.get('slug')}"
    return None


def calculate_tax(
    mass: int,
    year: int,
    fuel: str,
    co2_method: str = "wltp",
    co2: int = 0,
    vehicletype: str = "henkiloauto",
    rawresponse: bool = False,
) -> Optional[Dict[str, Decimal]]:
    # https://www.traficom.fi/fi/liikenne/autoilijat/ajoneuvon-verotus/ajoneuvoveron-maara#75745-1

    # we only support henkilöautos
    if vehicletype != "henkiloauto":
        return None

    USE_CO2_TAX = True
    if (int(mass) <= 2500 and int(year) < 2001) or (int(mass) > 2500 and int(year) < 2002) or co2 == 0:
        USE_CO2_TAX = False

    if USE_CO2_TAX:
        basetax = base_tax_from_co2(co2_method, co2)
    elif fuel == "sähkö":
        # FIXME: it's actually before 2021-09-30 but close enough
        basetax = 106.215 if year < 2022 else 171.185
    else:
        basetax = base_tax_from_mass(mass)

    yearlytax = {}
    yearlytax["base"] = basetax
    if fuel == "diesel" or fuel == "sähkö":
        yearlytax["fuel"] = round(fuel_tax_from_mass(mass=mass, fuel_type=fuel) * 365, 3)

    return yearlytax


def get_motonet_info(licenseplate: str) -> Optional[dict]:
    # FIXME i guess this should be generated
    cookies = {
        "expire": "1705954960780",
    }

    params = {
        "locale": "fi",
        "registrationNumber": licenseplate,
    }

    info = requests.get(
        MOTONET_ENDPOINT,
        params=params,
        cookies=cookies,
        headers=DEFAULT_HEADERS,
    ).json()

    return info


def get_biltema_info(licenseplate: str) -> Optional[dict]:
    try:
        reko = requests.get(REKO_ENDPOINT.format(licenseplate=licenseplate), headers=DEFAULT_HEADERS).json()
    except Exception:
        return {}
    # reko2 = requests.get(
    #     REKO2_ENDPOINT.format(licenseplate=licenseplate),
    #     headers=DEFAULT_HEADERS,
    #     params={"market": "3", "language": "FI"},
    # ).json()
    # print(json.dumps(reko2, indent=2))
    return reko


def get_technical(licenseplate: str, rawresponse: bool = False) -> Optional[dict]:
    licenseplate = licenseplate.upper()
    motonet_info = get_motonet_info(licenseplate)
    biltema_info = get_biltema_info(licenseplate)

    if motonet_info:
        firstreg = datetime.datetime.strptime(motonet_info.get("registrationDate"), "%d.%m.%Y")
    elif biltema_info:
        firstreg = datetime.datetime.strptime(biltema_info.get("registrationDate"), "%Y%m%d")
    else:
        # we can return and go home, most probably there was no data available
        return None

    techdata = {
        "manufacturer": motonet_info.get("manufacturerName", ""),
        "model": motonet_info.get("model", "") or biltema_info.get("nameOfTheCar"),
        "type": motonet_info.get("type", ""),
        "year": biltema_info.get("modelYear", firstreg.year),
        "year_is_approximate": biltema_info.get("modelYear") is None,
        "power": motonet_info.get("powerKw") or biltema_info.get("powerKw"),
        "displacement": motonet_info.get("displacement"),
        "cylindercount": motonet_info.get("cylinders"),
        "fueltype": motonet_info.get("fuel", "").lower()
        if motonet_info.get("fuel", "") is not None
        else biltema_info.get("fuel").lower(),
        "drivetype": biltema_info.get("impulsionType", "").lower(),
        "transmission": "automaatti" if biltema_info.get("gearBox", "").lower() == "automaattinen" else "manuaali",
        "enginecode": motonet_info.get("engineCode", "").replace(" ", "") or biltema_info.get("engineCode"),
        "weight": biltema_info.get("weightKg"),
        "maxweight": biltema_info.get("maxWeightKg", 0),
        "length": biltema_info.get("lenght"),
        "registrationdate": firstreg,
        "vin": motonet_info.get("VIN") or biltema_info.get("chassieNumber"),
        "suomiauto": True if biltema_info.get("imported") == "true" else False,
    }

    filter = {
        "vin": techdata.get("vin"),
        "omamassa": techdata.get("weight"),
        "kayttoonottopvm": biltema_info.get("registrationDate"),
    }

    try:
        req = requests.post(DSG_ENDPOINT, json=filter, timeout=10)
        dsg_data = req.json()
        count = len(dsg_data)
        if count == 1:
            dsg_data = dsg_data[0]
            dsg_data["count"] = 1
        else:
            dsg_data = {}
            dsg_data["count"] = count
    except Exception as ex:
        dsg_data = {}
        dsg_data["exception"] = repr(ex)
        dsg_data["count"] = 0
    techdata |= {
        "co2": dsg_data.get("WLTP_Co2") or dsg_data.get("NEDC_Co2"),
        "location": dsg_data.get("kunta_fi"),
        "color": dsg_data.get("vari_fi"),
        "mileage": dsg_data.get("matkamittarilukema"),
        "dsg_data_count": dsg_data.get("count", 0),
    }

    if rawresponse:
        print(json.dumps(motonet_info, indent=2))
        print(json.dumps(biltema_info, indent=2))
        print(json.dumps(dsg_data, indent=2))

    # hack this
    if techdata.get("fueltype") == "sähkö":
        techdata["transmission"] = "automaatti"
        techdata["co2"] = 0

    return techdata


def get_leima(licenseplate: str) -> Optional[str]:
    # new! a feature to scrape internet and get the next inspection date
    req = requests.post(LEIMA_ENDPOINT, json={"registrationNumber": licenseplate.upper()})
    leima_info = json.loads(req.text)
    if leima_info:
        return leima_info.get("nextInspectionBefore", "")
    return None


@plugin.rule(r"!leima\s*([a-zA-Z0-9\-]*)\s*([0-9\-]*)")
def handle_leima(bot, trigger) -> None:
    # either set the next leima date for a plate or display the next one for the plate
    # old stuff, maybe get rid of this if the new scraping works well enough
    state = db.SopelDB(bot.config)
    chan = state.get_channel_slug(trigger.sender)
    leimas = state.get_channel_value(chan, "leima", {})

    # TODO? normalize channel slug to avoid problems with storage later on
    licenseplate = trigger.group(1)

    # tell the user how to use
    if not licenseplate:
        return bot.say(f"Kokeile {trigger.group(0)} <kilpi> [uusi_määräaika]")

    # has the user provided a new date to save?
    if new_date := trigger.group(2):
        leimas[licenseplate] = new_date
        # sopel channel values need to be json serializable so we'll parse this as datetime later
        state.set_channel_value(chan, "leima", leimas)
        return bot.say(f"{licenseplate.upper()}: seuraava katsastus: {new_date}")

    # no new date, just display the current one
    leima_date = get_leima(licenseplate)
    if leima_date:
        try:
            time_to_leima = datetime.datetime.fromisoformat(leima_date) - datetime.datetime.today()
            bot.say(f"{licenseplate.upper()}: Katsastettava viimeistään {leima_date} ({time_to_leima.days} päivää)")
            return
        except ValueError:
            bot.say(f"Tuli hassua dataa netistä: {leima_date}...")

    # if not, is the plate already in the db?
    if licenseplate in leimas:
        leima_date = leimas.get(licenseplate)
        try:
            time_to_leima = datetime.datetime.fromisoformat(leima_date) - datetime.datetime.today()
            bot.say(f"{licenseplate.upper()}: Katsastettava viimeistään {leima_date} ({time_to_leima.days} päivää)")
        except ValueError:
            bot.say(f"Erikoinen päivämäärä toi {leima_date}...")
    else:
        bot.say(f"Ei oo kerrottu milloin {licenseplate.upper()} pitää katsastaa :(")


@plugin.commands("rekisteri")
@plugin.commands("rekkari")
@plugin.example(
    "!rekisteri bey-830",
    "BEY-830: VOLVO S40 II (MS) 2.0 D 2008. 100 kW 1998 cm³ 4-syl diesel etuveto (D4204T). Ajoneuvovero 609,55 EUR/vuosi, CO² 153 g/km (NEDC), kulutus 5,8/4,8/7,6 l/100 km. Oma/kokonaismassa 1459/1940 kg, pituus 4480 mm. Ensirekisteröinti 4.10.2007, VIN YV1MS754182368635, suomiauto",
    online=True,
)
def print_technical(bot, trigger) -> None:
    licenseplate = trigger.group(2)
    if not licenseplate:
        res = requests.get(DSG_ENDPOINT + "/stats").json()
        return bot.say(f"Autoja on väliltä {res.get('min_date')} - {res.get('max_date')}.")
    techdata = get_technical(licenseplate)
    if techdata is not None:
        try:
            taxdata = calculate_tax(
                mass=int(techdata.get("maxweight")),
                year=int(techdata.get("year")),
                fuel=techdata.get("fueltype"),
                co2=int(techdata.get("co2")),
            )
        except Exception:
            taxdata = None

        if taxdata is not None:
            if taxdata.get("fuel"):
                emissionspart = f" Ajoneuvovero {taxdata.get('fuel')} + {taxdata.get('base')} € vuodessa"
            else:
                emissionspart = f" Ajoneuvovero {taxdata.get('base')} € vuodessa"
            if techdata.get("co2"):
                emissionspart += f", CO² {techdata.get('co2')} g/km."
            else:
                emissionspart = ", ei päästöjä."
        else:
            emissionspart = " Ei päästötietoja."

        # :D utf-8 and all
        if techdata.get("fueltype") != "s\u00e4hk\u00f6":
            fuelpart = (
                f"{techdata.get('displacement')} cm³ {techdata.get('cylindercount')}-syl {techdata.get('fueltype')}"
            )
        else:
            fuelpart = f"{techdata.get('fueltype')}"

        if techdata.get("weight"):
            masspart = f" Oma/kokonaismassa {techdata.get('weight')}/{techdata.get('maxweight')} kg, pituus {techdata.get('length')} mm."
        else:
            masspart = ""
        result = f"{licenseplate.upper()}: {techdata.get('manufacturer')} {techdata.get('model')} {techdata.get('type')} {techdata.get('year')}. {techdata.get('power')} kW {fuelpart} {techdata.get('transmission')} {techdata.get('drivetype')} ({techdata.get('enginecode')}).{emissionspart}{masspart} Ensirekisteröinti {techdata.get('registrationdate').strftime('%-d.%-m.%Y')}, VIN {techdata.get('vin')}{', suomiauto' if techdata.get('suomiauto') else ''}."

        if techdata.get("dsg_data_count") == 1:
            result += f" Väri {techdata.get('color').lower()} ja koti {techdata.get('location')}. Ajettu {techdata.get('mileage')} km."
        elif techdata.get("dsg_data_count") > 1:
            result += f" Traficomin datassa {techdata.get('dsg_data_count')} samanlaista autoa."
        bot.say(result)
    else:
        bot.say(f"{licenseplate.upper()}: Varmaan joku romu mihin ei saa enää ees varaosia :-(")

    ad_links = []
    nettiauto_url = get_nettix_link(bot, licenseplate)
    if nettiauto_url:
        ad_links.append(nettiauto_url)
    if "manufacturer" in techdata and "year" in techdata:
        huutokaupatcom_url = get_huutokaupatcom_link(
            techdata.get("manufacturer"), int(techdata.get("year")), licenseplate
        )
        if huutokaupatcom_url:
            ad_links.append(huutokaupatcom_url)
    if ad_links:
        if techdata is not None:
            bot.say(f"On muuten myynnissä: {' ja '.join(ad_links)}")
        else:
            bot.say(f"On kuitenkin myynnissä: {' ja '.join(ad_links)}")


if __name__ == "__main__":
    try:
        from sopel.test_tools import run_example_tests

        run_example_tests(__file__)
    except Exception:
        pass

    # print(get_huutokaupatcom_link("volkswagen", 2015, "flp-912"))
