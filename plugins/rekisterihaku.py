# coding=utf8
"""
    made by tuplis 2021-2024
"""

from sopel import plugin, tools
from bs4 import BeautifulSoup
from typing import Dict, Optional
from decimal import Decimal

import requests
import json
import datetime

BILTEMA_ENDPOINT = 'https://reko.biltema.com/v1/Reko/carinfo/{licenseplate}/3/fi'
MOTONET_ENDPOINT = 'https://www.motonet.fi/api/vehicleInfo/registrationNumber/FI/{licenseplate}?locale=fi'
DSG_ENDPOINT = "http://localhost:8000"
DEFAULT_HEADERS: Dict[str, str] = {}

NEDC_MAP = {
    0: 53.29,
    1: 53.65,
    2: 54.02,
    3: 54.38,
    4: 54.75,
    5: 55.11,
    6: 55.48,
    7: 55.84,
    8: 56.21,
    9: 56.57,
    10: 57.30,
    11: 57.67,
    12: 58.03,
    13: 58.40,
    14: 58.76,
    15: 59.49,
    16: 59.86,
    17: 60.22,
    18: 60.59,
    19: 61.32,
    20: 61.68,
    21: 62.05,
    22: 62.78,
    23: 63.14,
    24: 63.51,
    25: 64.24,
    26: 64.60,
    27: 65.33,
    28: 65.70,
    29: 66.43,
    30: 66.79,
    31: 67.52,
    32: 67.89,
    33: 68.62,
    34: 68.98,
    35: 69.71,
    36: 70.08,
    37: 70.81,
    38: 71.54,
    39: 71.90,
    40: 72.63,
    41: 73.36,
    42: 73.73,
    43: 74.46,
    44: 75.19,
    45: 75.92,
    46: 76.28,
    47: 77.01,
    48: 77.74,
    49: 78.47,
    50: 79.20,
    51: 79.93,
    52: 80.66,
    53: 81.39,
    54: 81.76,
    55: 82.49,
    56: 83.58,
    57: 84.31,
    58: 85.04,
    59: 85.77,
    60: 86.50,
    61: 87.23,
    62: 87.96,
    63: 88.69,
    64: 89.42,
    65: 90.52,
    66: 91.25,
    67: 91.98,
    68: 93.07,
    69: 93.80,
    70: 94.53,
    71: 95.63,
    72: 96.36,
    73: 97.09,
    74: 98.18,
    75: 98.91,
    76: 100.01,
    77: 101.10,
    78: 101.83,
    79: 102.93,
    80: 103.66,
    81: 104.75,
    82: 105.85,
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
    111: 139.43,
    112: 140.52,
    113: 141.98,
    114: 143.44,
    115: 144.90,
    116: 146.36,
    117: 147.46,
    118: 148.92,
    119: 150.38,
    120: 151.84,
    121: 153.30,
    122: 154.76,
    123: 156.22,
    124: 158.04,
    125: 159.50,
    126: 160.96,
    127: 162.42,
    128: 164.25,
    129: 165.71,
    130: 167.17,
    131: 168.99,
    132: 170.45,
    133: 172.28,
    134: 173.74,
    135: 175.56,
    136: 177.02,
    137: 178.85,
    138: 180.67,
    139: 182.13,
    140: 183.96,
    141: 185.78,
    142: 187.61,
    143: 189.43,
    144: 191.26,
    145: 193.08,
    146: 194.91,
    147: 196.73,
    148: 198.56,
    149: 200.38,
    150: 202.21,
    151: 204.40,
    152: 206.22,
    153: 208.05,
    154: 210.24,
    155: 212.06,
    156: 214.25,
    157: 216.08,
    158: 218.27,
    159: 220.09,
    160: 222.28,
    161: 224.11,
    162: 226.30,
    163: 228.49,
    164: 230.68,
    165: 232.87,
    166: 234.69,
    167: 236.88,
    168: 239.07,
    169: 241.26,
    170: 243.45,
    171: 246.01,
    172: 248.20,
    173: 250.39,
    174: 252.58,
    175: 254.77,
    176: 257.32,
    177: 259.51,
    178: 261.70,
    179: 264.26,
    180: 266.45,
    181: 269.00,
    182: 271.19,
    183: 273.75,
    184: 276.30,
    185: 278.49,
    186: 281.05,
    187: 283.60,
    188: 286.16,
    189: 288.35,
    190: 290.90,
    191: 293.46,
    192: 296.01,
    193: 298.57,
    194: 301.12,
    195: 303.68,
    196: 306.23,
    197: 309.15,
    198: 311.71,
    199: 313.90,
    200: 316.09,
    201: 318.28,
    202: 320.10,
    203: 322.29,
    204: 324.48,
    205: 326.67,
    206: 328.50,
    207: 330.69,
    208: 332.88,
    209: 335.07,
    210: 337.26,
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
    0: 53.29,
    1: 53.29,
    2: 53.65,
    3: 54.02,
    4: 54.38,
    5: 54.75,
    6: 55.11,
    7: 55.48,
    8: 55.48,
    9: 55.84,
    10: 56.21,
    11: 56.57,
    12: 56.94,
    13: 57.30,
    14: 57.67,
    15: 58.03,
    16: 58.40,
    17: 58.76,
    18: 59.13,
    19: 59.49,
    20: 59.86,
    21: 60.22,
    22: 60.59,
    23: 60.95,
    24: 61.32,
    25: 61.68,
    26: 62.05,
    27: 62.41,
    28: 62.78,
    29: 63.14,
    30: 63.51,
    31: 64.24,
    32: 64.60,
    33: 64.97,
    34: 65.33,
    35: 65.70,
    36: 66.06,
    37: 66.43,
    38: 67.16,
    39: 67.52,
    40: 67.89,
    41: 68.25,
    42: 68.98,
    43: 69.35,
    44: 69.71,
    45: 70.08,
    46: 70.81,
    47: 71.17,
    48: 71.54,
    49: 72.27,
    50: 72.63,
    51: 73.00,
    52: 73.73,
    53: 74.09,
    54: 74.46,
    55: 75.19,
    56: 75.55,
    57: 76.28,
    58: 76.65,
    59: 77.38,
    60: 77.74,
    61: 78.47,
    62: 78.84,
    63: 79.57,
    64: 79.93,
    65: 80.66,
    66: 81.03,
    67: 81.76,
    68: 82.12,
    69: 82.85,
    70: 83.58,
    71: 83.95,
    72: 84.68,
    73: 85.04,
    74: 85.77,
    75: 86.50,
    76: 86.87,
    77: 87.60,
    78: 88.33,
    79: 89.06,
    80: 89.42,
    81: 90.15,
    82: 90.88,
    83: 91.61,
    84: 92.34,
    85: 93.07,
    86: 93.44,
    87: 94.17,
    88: 94.90,
    89: 95.63,
    90: 96.36,
    91: 97.09,
    92: 97.82,
    93: 98.55,
    94: 99.28,
    95: 100.01,
    96: 100.74,
    97: 101.47,
    98: 102.20,
    99: 102.93,
    100: 103.66,
    101: 104.39,
    102: 105.48,
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
}


def base_tax_from_mass(mass: int) -> Optional[float]:
    if (mass <= 1300):
        return 0.610
    elif (mass > 1300 and mass <= 1400):
        return 0.640
    elif (mass > 1400 and mass <= 1500):
        return 0.672
    elif (mass > 1500 and mass <= 1600):
        return 0.706
    elif (mass > 1600 and mass <= 1700):
        return 0.742
    elif (mass > 1700 and mass <= 1800):
        return 0.780
    elif (mass > 1800 and mass <= 1900):
        return 0.820
    elif (mass > 1900 and mass <= 2000):
        return 0.862
    elif (mass > 2000 and mass <= 2100):
        return 0.906
    elif (mass > 2100 and mass <= 2200):
        return 0.952
    elif (mass > 2200 and mass <= 2300):
        return 1.000
    elif (mass > 2300 and mass <= 2400):
        return 1.050
    elif (mass > 2400 and mass <= 2500):
        return 1.102
    elif (mass > 2500 and mass <= 2600):
        return 1.156
    elif (mass > 2600 and mass <= 2700):
        return 1.212
    elif (mass > 2700 and mass <= 2800):
        return 1.270
    elif (mass > 2800 and mass <= 2900):
        return 1.330
    elif (mass > 2900 and mass <= 3000):
        return 1.392
    elif (mass > 3000 and mass <= 3100):
        return 1.456
    elif (mass > 3100 and mass <= 3200):
        return 1.522
    elif (mass > 3200 and mass <= 3300):
        return 1.590
    elif (mass > 3300 and mass <= 3400):
        return 1.660
    elif (mass > 3400):
        return 1.732
    else:
        return None


def base_tax_from_co2(measurement_type: str, co2: int) -> Optional[float]:
    if co2 > 400:
        return round(1.793 * 365, 2)

    if measurement_type == 'nedc':
        return NEDC_MAP[co2]
    if measurement_type == 'wltp':
        return WLTP_MAP[co2]
    else:
        return None


def fuel_tax_from_mass(mass: int, fuel_type: str = "diesel") -> Optional[float]:
    if fuel_type != "diesel":
        return None

    # you know, float arithmetic
    kg = -(mass // -100)
    return kg * FUEL_TAX_MAP['diesel']


def configure(config):
    pass


def setup(bot):
    if 'nettix_token' not in bot.memory:
        bot.memory['nettix_token'] = tools.SopelMemory()


def refresh_nettix_token(bot) -> bool:
    res = requests.post('https://auth.nettix.fi/oauth2/token', data={'grant_type': 'client_credentials'})
    token = json.loads(res.text)
    bot.memory['nettix_token']['access_token'] = token.get('access_token', '')
    bot.memory['nettix_token']['expires_in'] = datetime.datetime.now() + datetime.timedelta(seconds=token.get('expires_in', ''))
    return res.status_code == 200


def get_nettix_link(bot, licenseplate) -> Optional[str]:
    if bot.memory['nettix_token'].get('expires_in', datetime.datetime.now()) <= datetime.datetime.now():
        if not refresh_nettix_token(bot):
            bot.say("oops, nettix api broken")

    headers = {
        "Accept": "application/json",
        "X-Access-Token": bot.memory['nettix_token'].get('access_token')
    }

    payload = {
        'identificationList': licenseplate
    }

    res = requests.get('https://api.nettix.fi/rest/car/search', params=payload, headers=headers)
    nettix_ad = json.loads(res.text)
    if nettix_ad:
        return nettix_ad[0].get('adUrl')
    else:
        return None


def get_tori_link(licenseplate: str) -> Optional[str]:
    payload = {
        'hakusana': licenseplate
    }

    res = requests.get('https://autot.tori.fi/vaihtoautot', params=payload)
    soup = BeautifulSoup(res.text, features="lxml")
    data = json.loads(soup.find('script', id="__NEXT_DATA__").string)

    try:
        # yeah i know
        link = data['props']['pageProps']['initialReduxState']['search']['result']['list_ads'][0]['share_link']
    except Exception:
        return None

    return link


def calculate_tax(mass: int, year: int, fuel: str, nedc_co2: int = 0, wltp_co2: int = 0, vehicletype: str = "henkiloauto", rawresponse: bool = False) -> Optional[Decimal]:
    # https://www.traficom.fi/fi/liikenne/tieliikenne/ajoneuvoveron-rakenne-ja-maara
    # we only support henkilöautos
    if vehicletype != "henkiloauto":
        return None

    if (int(mass) <= 2500 and int(year) < 2001) or (int(mass) > 2500 and int(year) < 2002):
        USE_CO2_TAX = False
    else:
        USE_CO2_TAX = True

    if USE_CO2_TAX:
        if nedc_co2:
            basetax = base_tax_from_co2("nedc", nedc_co2)
        elif wltp_co2:
            basetax = base_tax_from_co2("wltp", wltp_co2)
        else:
            basetax = base_tax_from_mass(mass) * 365
    else:
        basetax = base_tax_from_mass(mass) * 365

    yearlytax = {}
    yearlytax['base'] = basetax
    if fuel == "diesel":
        yearlytax['fuel'] = round(fuel_tax_from_mass(mass) * 365, 2)

    return yearlytax


def get_technical(licenseplate: str, rawresponse: bool = False) -> Optional[dict]:
    # FIXME i guess this should be generated
    cookies = {
        "expire": "1705954960780",
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    req = requests.get(MOTONET_ENDPOINT.format(licenseplate=licenseplate.upper()), cookies=cookies, headers=headers)
    motonet_info = json.loads(req.text)
    if rawresponse:
        print(json.dumps(motonet_info, indent=2))

    req = requests.get(BILTEMA_ENDPOINT.format(licenseplate=licenseplate.upper()), headers=headers)
    try:
        biltema_info = json.loads(req.text)
        if rawresponse:
            print(json.dumps(biltema_info, indent=2))
    except Exception:
        biltema_info = {}

    if motonet_info:
        firstreg = datetime.datetime.strptime(motonet_info.get('registrationDate'), '%d.%m.%Y')
    elif biltema_info:
        firstreg = datetime.datetime.strptime(biltema_info.get('registrationDate'), '%Y%m%d')
    else:
        # we can return and go home, most probably there was no data available
        return None

    params = {
        "vin": motonet_info.get('VIN'),
        "omamassa": biltema_info.get('weightKg'),
        "kayttoonottopvm": biltema_info.get('registrationDate')
    }
    try:
        req = requests.post(DSG_ENDPOINT, json=params, timeout=5)
        dsg_data = req.json()
        count = len(dsg_data)
        if count == 1:
            dsg_data = dsg_data[0]
            dsg_data['count'] = 1
        else:
            dsg_data = {}
            dsg_data['count'] = count
    except Exception as ex:
        dsg_data = {}
        dsg_data['exception'] = repr(ex)
        dsg_data['count'] = 0

    if rawresponse:
        print(json.dumps(dsg_data))

    techdata = {
        'manufacturer': motonet_info.get('manufacturerName', ""),
        'model': motonet_info.get('model', "") or biltema_info.get('nameOfTheCar'),
        'type': motonet_info.get('type', ""),
        'year': biltema_info.get('modelYear', None) or f'~{firstreg.year}',
        'power': motonet_info.get('powerKw') or biltema_info.get('powerKw'),
        'displacement': motonet_info.get('displacement'),
        'cylindercount': motonet_info.get('cylinders'),
        'fueltype': motonet_info.get('fuel', '').lower() if motonet_info.get('fuel', '') is not None else biltema_info.get('fuel').lower(),
        'drivetype': biltema_info.get('impulsionType', '').lower(),
        'transmission': 'automaatti' if biltema_info.get('gearBox', '').lower() == 'automaattinen' else 'manuaali',
        'enginecode': motonet_info.get('engineCode', '').replace(' ', '') or biltema_info.get('engineCode'),
        'weight': biltema_info.get('weightKg'),
        'maxweight': biltema_info.get('maxWeightKg'),
        'length': biltema_info.get('lenght'),
        'registrationdate': firstreg,
        'vin': motonet_info.get('VIN') or biltema_info.get('chassieNumber'),
        'suomiauto': True if biltema_info.get('imported') == 'true' else False,
        'co2': dsg_data.get('Co2'),
        'location': dsg_data.get('kunta_fi'),
        'color': dsg_data.get('vari_fi'),
        'mileage': dsg_data.get('matkamittarilukema'),
        'dsg_data_count': dsg_data.get('count', 0)
    }

    return techdata


@plugin.commands('rekisteri')
@plugin.commands('rekkari')
@plugin.example(
    '!rekisteri bey-830',
    'BEY-830: VOLVO S40 II (MS) 2.0 D 2008. 100 kW 1998 cm³ 4-syl diesel etuveto (D4204T). Ajoneuvovero 609,55 EUR/vuosi, CO² 153 g/km (NEDC), kulutus 5,8/4,8/7,6 l/100 km. Oma/kokonaismassa 1459/1940 kg, pituus 4480 mm. Ensirekisteröinti 4.10.2007, VIN YV1MS754182368635, suomiauto',
    online=True)
def print_technical(bot, trigger) -> None:
    licenseplate = trigger.group(2)
    techdata = get_technical(licenseplate)
    if techdata is not None:
        try:
            taxdata = calculate_tax(int(techdata.get('maxweight')), int(techdata.get('year')), techdata.get('fueltype'), int(techdata.get('co2')))
        except Exception:
            taxdata = None

        if taxdata is not None:
            if taxdata.get('fuel'):
                emissionspart = f" Ajoneuvovero {taxdata.get('fuel')} + {taxdata.get('base')} € vuodessa"
            else:
                emissionspart = f" Ajoneuvovero {taxdata.get('base')} € vuodessa"
            if techdata.get('co2'):
                emissionspart += f", CO² {techdata.get('co2')} g/km."
            else:
                emissionspart = ", ei päästöjä."
        else:
            emissionspart = " Ei päästötietoja."

        # :D utf-8 and all
        if techdata.get("fueltype") != "s\u00e4hk\u00f6":
            fuelpart = f"{techdata.get('displacement')} cm³ {techdata.get('cylindercount')}-syl {techdata.get('fueltype')}"
        else:
            fuelpart = f"{techdata.get('fueltype')}"

        if techdata.get('weight'):
            masspart = f" Oma/kokonaismassa {techdata.get('weight')}/{techdata.get('maxweight')} kg, pituus {techdata.get('length')} mm."
        else:
            masspart = ""
        result = f"{licenseplate.upper()}: {techdata.get('manufacturer')} {techdata.get('model')} {techdata.get('type')} {techdata.get('year')}. {techdata.get('power')} kW {fuelpart} {techdata.get('transmission')} {techdata.get('drivetype')} ({techdata.get('enginecode')}).{emissionspart}{masspart} Ensirekisteröinti {techdata.get('registrationdate').strftime('%-d.%-m.%Y')}, VIN {techdata.get('vin')}{', suomiauto' if techdata.get('suomiauto') else ''}."

        if techdata.get('dsg_data_count') == 1:
            result += f" Väri {techdata.get('color').lower()} ja koti {techdata.get('location')}. Ajettu {techdata.get('mileage')} km."
        elif techdata.get('dsg_data_count') > 1:
            result += f" Traficomin datassa {techdata.get('dsg_data_count')} samanlaista autoa."
        bot.say(result)
    else:
        bot.say(f"{licenseplate.upper()}: Varmaan joku romu mihin ei saa enää ees varaosia :-(")

    ad_links = []
    nettiauto_url = get_nettix_link(bot, licenseplate)
    tori_url = get_tori_link(licenseplate)
    if nettiauto_url:
        ad_links.append(nettiauto_url)
    if tori_url:
        ad_links.append(tori_url)
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

    # print(get_technical(licenseplate="oxg-353", rawresponse=True))
    # print(get_emissions(licenseplate="gfs-10"))
    # print(get_nettix_token())
