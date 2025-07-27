import os
#from builtins import str

import sys
import sqlite3
import math

from edtime import EDTime
from edrlog import EDR_LOG



class EDRRawDepletables(object):
    
    HOTSPOTS = [
        ('Sol', 'Europa', 0.13, 2528, 'ice geysers [permit]', -1), # gone?
        ('Sol', 'Actae', 0.009, 18674, 'ice fumaroles [permit]', -1), # gone?
        ('Beta Hydri', '7 C', 0.09, 2105, 'gas vents [permit]', 1), # there
        ('LHS 278', '7 A', 0.03, 462, 'ice geysers', 0), # TODO
        ('Malina', 'AB 5 A', 0.06, 1260, 'ice geysers', 0), #gone?
        ('Malina', 'AB 5 B', 0.07, 1265, 'ice geysers', 1), # there
        ('LP 102-320', '1', 0.54, 9, 'rock fumaroles', -1), # gone?
        ('LHS 2405', 'B 7 A', 0.11, 684, 'ice geysers', 1),  # there?
        ('HIP 35755', '6 C', 0.09, 723, 'ice fumaroles', 1), # there
        ('HIP 35755', '7 A', 0.12, 964, 'lava spouts', 1), # there
        ('LTT 13904', 'B 1 A', 0.10, 1918, 'rock fumaroles', 0),
        ('LP 499-54', '7 E', 0.08, 973, 'ice geysers', 0),
        ('Meenates', '4 A', 0.04, 1145, 'ice geysers', 0),
        ('Vamm', 'B 2 A', 0.13, 21974, 'ice geysers', 0),
        ('Vamm', 'B 3 A', 0.03, 23563, 'ice geysers', 0),
        ('LTT 13904', 'B 1 A', 0.11, 3637, 'rock fumarole', 0),
        ('LTT 13904', 'B 1 A', 0.10, 1870, 'gas vents', 0),
        ('Beditjari', 'A 4 B', 0.06, 882, 'ice geysers', 0),
        ('Beditjari', 'A 4 C', 0.05, 881, 'ice geysers', 0),
        ('Marki', '8 A', 0.09, 519, 'ice geysers', 0),
        ('Exioce', 'Boston\'s Wreck', 0.09, 294, 'gas vents', 0),
        ('Exioce', 'Boston\'s Wreck', 0.09, 294, 'lava spouts', 0),
        ('Exioce', '4 A A', 0.06, 1625, 'rock fumarole', 0),
        ('HIP 41181', 'A 1 A', 0.12, 1025, 'lava spouts', 0),
        ('CD-58 4207', '6 A', 0.06, 2692, 'ice lava', 0),
        ('CD-58 4207', '6 A', 0.06, 2692, 'ice fumarole', 0),
        ('CD-58 4207', '6 B', 0.04, 2692, 'gas vents', 0),
        ('HIP 111755', 'A 1', 0.29, 11, 'rock fumarole', 0),
        ('Ngere', 'AB 1 A', 0.05, 3639, 'ice geysers', 0),
        ('Ngere', 'AB 1 B', 0.05, 3640, 'ice geysers', 0),
        ('Nortes', '2 C', 0.08, 849, 'rock fumarole', 0),
        ('Nortes', '2 D', 0.07, 849, 'lava spouts', 0),
        ('Jardonnere', '6 B', 0.08, 865, 'ice geysers', 0),
        ('Jardonnere', '6 E A', 0.03, 863, 'ice geysers', 0),
        ('Upsilon Phoenicis', '1', 1.72, 342, 'lava spouts', 0),
        ('Tujing', '2 A', 0.11, 75, 'gas vents', 0),
        ('Tujing', '7 F', 0.09, 1223, 'ice geysers', 0),
        ('Tujing', '8 A', 0.06, 1698, 'ice geysers', 0),
        ('BD+65 210', '7 A', 0.04, 998, 'ice geysers', 0),
        ('G 203-47', '6 A', 0.14, 1599, 'ice geysers', 0),
        ('Buzhang Ku', '5 A', 1457, 0.03, 'ice geysers', 0),
        ('Buzhang Ku', '4 A', 0.03, 874, 'ice geysers', 0),
        ('Siksikas', '8 A', 0.06, 796, 'ice geysers', 0),
        ('Fortuna', 'AB 1 A', 0.13, 5816, 'ice geysers', 0),
        ('Juipedun', 'A 1', 0.18, 7, 'rock fumaroles', 0),
        ('Fortuna', 'AB 1 B', 0.12, 5856, 'ice geysers', 0),
        ('Guttors', 'ABC 2 A', 0.05, 2684, 'ice geysers', 0),
        ('G 123-16', '7 B', 0.07, 1029, 'ice geysers', 0),
        ('Tocorii', '9 C', 0.07, 1214, 'ice geysers', 0),
        ('Dassareti', '3 B', 0.14, 1527, 'ice geysers', 0),
        ('G 203-47', '6 B', 0.11, 1600, 'ice geysers', 0),
        ('BD+65 210', '7 B', 0.04, 998, 'ice geysers', 0),
        ('Gliese 3299', 'c 3 B', 0.04, 29691, 'ice geysers', 0),
        ('G 123-16', '7 C', 0.08, 1027, 'ice geysers', 0),
        ('Banki', 'A 3 A', 0.04, 1752, 'ice geysers', 0),
        ('Buzhang Ku', '3 A', 0.05, 853, 'ice geysers', 0),
        ('G 203-47', '9 A', 0.08, 2312, 'ice geysers', 0),
        ('Ch\'eng', '6 C', 0.04, 3715, 'ice geysers', 0),
        ('61 Cygni', 'A 1', 0.83, 8, 'rock fumaroles', 0),
        ('Cofan', '5 B', 0.06, 1707, 'ice geysers', 0),
        ('Ch\'eng', '6 B', 0.05, 3715, 'ice geysers', 0),
        ('He Qiong', '6 A', 0.05, 1049, 'ice geysers', -1), # gone
        ('Buzhang Ku', '3 B', 0.05, 854, 'ice geysers', 0),
        ('Banki', 'A 3 B', 0.03, 1752, 'ice geysers', 0),
        ('HIP 42455', 'B 2 A', 0.11, 16820, 'ice geysers', 0),
        ('LTT 4599', '6 A', 0.11, 2400, 'ice geysers', 0),
        ('LP 244-47', '5 A', 0.06, 1108, 'ice geysers', 0),
    ]

    POI_LUT = { 
        "sol europa ice geysers":{ 
            "system":"Sol",
            "planet":"Europa"
        },
        "sol actae ice fumarole":{ 
            "system":"Sol",
            "planet":"Actae"
        },
        "beta hydri 7 c gas vents":{ 
            "system":"Beta Hydri",
            "planet":"7 C"
        },
        "lhs 278 7 a ice geysers":{ 
            "system":"LHS 278",
            "planet":"7 A"
        },
        "malina ab 5 a ice geysers":{ 
            "system":"Malina",
            "planet":"AB 5 A"
        },
        "malina ab 5 b ice geysers":{ 
            "system":"Malina",
            "planet":"AB 5 B"
        },
        "lp 102-320 1 rock fumarole":{ 
            "system":"LP 102-320",
            "planet":"1"
        },
        "lhs 2405 b 7 a ice geysers":{ 
            "system":"LHS 2405",
            "planet":"B 7 A"
        },
        "hip 35755 6 c ice fumarole":{ 
            "system":"HIP 35755",
            "planet":"6 C"
        },
        "hip 35755 7 a lava spouts":{ 
            "system":"HIP 35755",
            "planet":"7 A"
        },
        "ltt 13904 b 1 a rock fumarole":{ 
            "system":"LTT 13904",
            "planet":"B 1 A"
        },
        "lp 499-54 7 e ice geysers":{ 
            "system":"LP 499-54",
            "planet":"7 E"
        },
        "meenates 4 a ice geysers":{ 
            "system":"Meenates",
            "planet":"4 A"
        },
        "vamm b 2 a ice geysers":{ 
            "system":"Vamm",
            "planet":"B 2 A"
        },
        "vamm b 3 a ice geysers":{ 
            "system":"Vamm",
            "planet":"B 3 A"
        },
        "ltt 13904 b 1 a gas vents":{ 
            "system":"LTT 13904",
            "planet":"B 1 A"
        },
        "beditjari a 4 b ice geysers":{ 
            "system":"Beditjari",
            "planet":"A 4 B"
        },
        "beditjari a 4 c ice geysers":{ 
            "system":"Beditjari",
            "planet":"A 4 C"
        },
        "marki 8 a ice geysers":{ 
            "system":"Marki",
            "planet":"8 A"
        },
        "exioce boston's wreck gas vents":{ 
            "system":"Exioce",
            "planet":"Boston's Wreck"
        },
        "exioce boston's wreck lava spouts":{ 
            "system":"Exioce",
            "planet":"Boston's Wreck"
        },
        "exioce 4 a a rock fumarole":{ 
            "system":"Exioce",
            "planet":"4 A A"
        },
        "hip 41181 a 1 a lava spouts":{ 
            "system":"HIP 41181",
            "planet":"A 1 A"
        },
        "cd-58 4207 6 a ice lava":{ 
            "system":"CD-58 4207",
            "planet":"6 A"
        },
        "cd-58 4207 6 a ice fumarole":{ 
            "system":"CD-58 4207",
            "planet":"6 A"
        },
        "cd-58 4207 6 b gas vents":{ 
            "system":"CD-58 4207",
            "planet":"6 B"
        },
        "hip 111755 a 1 rock fumarole":{ 
            "system":"HIP 111755",
            "planet":"A 1"
        },
        "ngere ab 1 a ice geysers":{ 
            "system":"Ngere",
            "planet":"AB 1 A"
        },
        "ngere ab 1 b ice geysers":{ 
            "system":"Ngere",
            "planet":"AB 1 B"
        },
        "nortes 2 c rock fumarole":{ 
            "system":"Nortes",
            "planet":"2 C"
        },
        "nortes 2 d lava spouts":{ 
            "system":"Nortes",
            "planet":"2 D"
        },
        "jardonnere 6 b ice geysers":{ 
            "system":"Jardonnere",
            "planet":"6 B"
        },
        "jardonnere 6 e a ice geysers":{ 
            "system":"Jardonnere",
            "planet":"6 E A"
        },
        "upsilon phoenicis 1 lava spouts":{ 
            "system":"Upsilon Phoenicis",
            "planet":"1"
        },
        "tujing 2 a gas vents":{ 
            "system":"Tujing",
            "planet":"2 A"
        },
        "tujing 7 f ice geysers":{ 
            "system":"Tujing",
            "planet":"7 F"
        },
        "tujing 8 a ice geysers":{ 
            "system":"Tujing",
            "planet":"8 A"
        },
        'bd+65 210 7 a ice geysers: ': {  "system": "BD+65 210", "planet": "7 A"},
        'g 203-47 6 a ice geysers: ': {  "system": "G 203-47", "planet": "6 A"},
        'buzhang ku 5 a ice geysers: ': {  "system": "Buzhang Ku", "planet": "5 A"},
        'buzhang ku 4 a ice geysers: ': {  "system": "Buzhang Ku", "planet": "4 A"},
        'siksikas 8 a ice geysers: ': {  "system": "Siksikas", "planet": "8 A"},
        'fortuna ab 1 a ice geysers: ': {  "system": "Fortuna", "planet": "AB 1 A"},
        'juipedun a 1 rock fumaroles: ': {  "system": "Juipedun", "planet": "A 1"},
        'fortuna ab 1 b ice geysers: ': {  "system": "Fortuna", "planet": "AB 1 B"},
        'guttors abc 2 a ice geysers: ': {  "system": "Guttors", "planet": "ABC 2 A"},
        'g 123-16 7 b ice geysers: ': {  "system": "G 123-16", "planet": "7 B"},
        'tocorii 9 c ice geysers: ': {  "system": "Tocorii", "planet": "9 C"},
        'dassareti 3 b ice geysers: ': {  "system": "Dassareti", "planet": "3 B"},
        'g 203-47 6 b ice geysers: ': {  "system": "G 203-47", "planet": "6 B"},
        'bd+65 210 7 b ice geysers: ': {  "system": "BD+65 210", "planet": "7 B"},
        'gliese 3299 c 3 b ice geysers: ': {  "system": "Gliese 3299", "planet": "c 3 B"},
        'g 123-16 7 c ice geysers: ': {  "system": "G 123-16", "planet": "7 C"},
        'banki a 3 a ice geysers: ': {  "system": "Banki", "planet": "A 3 A"},
        'buzhang ku 3 a ice geysers: ': {  "system": "Buzhang Ku", "planet": "3 A"},
        'g 203-47 9 a ice geysers: ': {  "system": "G 203-47", "planet": "9 A"},
        'ch\'eng 6 c ice geysers: ': {  "system": "Ch'eng", "planet": "6 C"},
        '61 cygni a 1 rock fumaroles: ': {  "system": "61 Cygni", "planet": "A 1"},
        'cofan 5 b ice geysers: ': {  "system": "Cofan", "planet": "5 B"},
        'ch\'eng 6 b ice geysers: ': {  "system": "Ch'eng", "planet": "6 B"},
        'he qiong 6 a ice geysers: ': {  "system": "He Qiong", "planet": "6 A"},
        'buzhang ku 3 b ice geysers: ': {  "system": "Buzhang Ku", "planet": "3 B"},
        'banki a 3 b ice geysers: ': {  "system": "Banki", "planet": "A 3 B"},
        'hip 42455 b 2 a ice geysers: ': {  "system": "HIP 42455", "planet": "B 2 A"},
        'ltt 4599 6 a ice geysers: ': {  "system": "LTT 4599", "planet": "6 A"},
        'lp 244-47 5 a ice geysers: ': {  "system": "LP 244-47", "planet": "5 A"},
    }

    CONCENTRATIONS = [
        (1, 'chromium', 0.076),
        (1, 'vanadium', 0.042),
        (1, 'arsenic', 0.016),
        (1, 'cadmium', 0.013),
        (1, 'molybdenum', 0.011),
        (1, 'antimony', 0.008),
        (2, 'chromium', 0.079),
        (2, 'manganese', 0.073),
        (2, 'vanadium', 0.043),
        (2, 'molybdenum', 0.011),
        (2, 'yttrium', 0.01),
        (2, 'tungsten', 0.01),
        (3, 'germanium', 0.057),
        (3, 'zinc', 0.054),
        (3, 'vanadium', 0.049),
        (3, 'molybdenum', 0.013),
        (3, 'yttrium', 0.012),
        (3, 'mercury', 0.009),
        (4, 'chromium', 0.055),
        (4, 'manganese', 0.051),
        (4, 'arsenic', 0.016),
        (4, 'molybdenum', 0.008),
        (4, 'ruthenium', 0.008),
        (4, 'tungsten', 0.007),
        (5, 'germanium', 0.036),
        (5, 'zinc', 0.034),
        (5, 'vanadium', 0.03),
        (5, 'tellurium', 0.009),
        (5, 'niobium', 0.008),
        (5, 'molybdenum', 0.008),
        (6, 'chromium', 0.055),
        (6, 'selenium', 0.042),
        (6, 'vanadium', 0.03),
        (6, 'cadmium', 0.009),
        (6, 'mercury', 0.005),
        (7, 'chromium', 0.096),
        (7, 'manganese', 0.088),
        (7, 'germanium', 0.044),
        (7, 'molybdenum', 0.014),
        (7, 'tin', 0.014),
        (7, 'tellurium', 0.011),
        (8, 'chromium', 0.054),
        (8, 'manganese', 0.05),
        (8, 'selenium', 0.041),
        (8, 'niobium', 0.008),
        (8, 'ruthenium', 0.007),
        (8, 'tin', 0.007),
        (9, 'chromium', 0.07),
        (9, 'zinc', 0.043),
        (9, 'zirconium', 0.018),
        (9, 'niobium', 0.011),
        (9, 'tungsten', 0.009),
        (9, 'technetium', 0.006),
        (10, 'chromium', 0.088),
        (10, 'zinc',  0.053),
        (10, 'selenium',  0.030),
        (10, 'cadmium',  0.015),
        (10, 'molybdenum', 0.013),
        (10, 'technetium', 0.007),
        (11, 'germanium', 0.057),
        (11, 'selenium', 0.030),
        (11, 'zirconium', 0.025),
        (11, 'niobium', 0.015),
        (11, 'tin', 0.013),
        (11, 'yttrium', 0.013),

        (12, 'chromium', 0.053),
        (12, 'manganese', 0.049),
        (12, 'selenium', 0.041),
        (12, 'cadmium', 0.009),
        (12, 'ruthenium', 0.007),
        (12, 'tin', 0.007),

        (13, 'manganese', 0.05),
        (13, 'selenium', 0.042),
        (13, 'germanium', 0.035),
        (13, 'niobium', 0.008),
        (13, 'ruthenium', 0.008),
        (13, 'tin', 0.007),

        (14, 'manganese', 0.05),
        (14, 'selenium', 0.042),
        (14, 'germanium', 0.035),
        (14, 'cadmium', 0.009),
        (14, 'yttrium', 0.007),
        (14, 'mercury', 0.005),

        (15, 'chromium', 0.055),
        (15, 'zinc', 0.033),
        (15, 'vanadium', 0.03),
        (15, 'molybdenum', 0.008),
        (15, 'antimony', 0.007),
        (15, 'tungsten', 0.007),

        (16, 'manganese', 0.052),
        (16, 'selenium', 0.043),
        (16, 'arsenic', 0.016),
        (16, 'cadmium', 0.01),
        (16, 'ruthenium', 0.008),
        (16, 'mercury', 0.006),

        (17, 'germanium', 0.057),
        (17, 'selenium', 0.03),
        (17, 'zirconium', 0.026),
        (17, 'niobium', 0.015),
        (17, 'tin', 0.014),
        (17, 'yttrium', 0.013),

        (18, 'chromium', 0.055),
        (18, 'zinc', 0.033),
        (18, 'vanadium', 0.03),
        (18, 'cadmium', 0.009),
        (18, 'yttrium', 0.007),
        (18, 'mercury', 0.005),

        (19, 'chromium', 0.054),
        (19, 'selenium', 0.042),
        (19, 'germanium', 0.035),
        (19, 'cadmium', 0.009),
        (19, 'Te', 0.009),
        (19, 'niobium', 0.008),

        (20, 'manganese', 0.05),
        (20, 'selenium', 0.042),
        (20, 'germanium', 0.035),
        (20, 'Te', 0.009),
        (20, 'tin', 0.007),
        (20, 'tungsten', 0.007),

        (21, 'chromium', 0.093),
        (21, 'zinc', 0.056),
        (21, 'germanium', 0.051),
        (21, 'molybdenum', 0.014),
        (21, 'tin', 0.013),
        (21, 'Po', 0.006),

        (22, 'chromium', 0.093),
        (22, 'zinc', 0.056),
        (22, 'germanium', 0.051),
        (22, 'molybdenum', 0.014),
        (22, 'tin', 0.013),
        (22, 'Po', 0.006),

        (23, 'chromium', 0.079),
        (23, 'germanium', 0.059),
        (23, 'zinc', 0.048),
        (23, 'antimony', 0.013),
        (23, 'molybdenum', 0.012),
        (23, 'tungsten', 0.010),

        (24, 'chromium', 0.086),
        (24, 'manganese', 0.079),
        (24, 'selenium', 0.029),
        (24, 'cadmium', 0.015),
        (24, 'mercury', 0.008),
        (24, 'technetium', 0.007),

        (25, 'chromium', 0.076),
        (25, 'germanium', 0.049),
        (25, 'arsenic', 0.022),
        (25, 'molybdenum', 0.011),
        (25, 'tin', 0.01),
        (25, 'yttrium', 0.01),

        (26, 'chromium', 0.076),
        (26, 'germanium', 0.049),
        (26, 'arsenic', 0.022),
        (26, 'molybdenum', 0.011),
        (26, 'tin', 0.01),
        (26, 'yttrium', 0.01),

        (27, 'germanium', 0.049),
        (27, 'zinc', 0.047),
        (27, 'vanadium', 0.042),
        (27, 'cadmium', 0.013),
        (27, 'ruthenium', 0.011),
        (27, 'tin', 0.01),

        (28, 'chromium', 0.095),
        (28, 'manganese', 0.087),
        (28, 'zinc', 0.057),
        (28, 'molybdenum', 0.014),
        (28, 'ruthenium', 0.013),
        (28, 'tungsten', 0.012),

        (29, 'manganese', 0.051),
        (29, 'zinc', 0.034),
        (29, 'zirconium', 0.014),
        (29, 'niobium', 0.008),
        (29, 'ruthenium', 0.008),
        (29, 'tungsten', 0.007),

        (30, 'manganese', 0.05),
        (30, 'selenium', 0.042),
        (30, 'vanadium', 0.03),
        (30, 'molybdenum', 0.008),
        (30, 'antimony', 0.007),
        (30, 'tin', 0.007),

        (31, 'manganese', 0.079),
        (31, 'germanium', 0.055),
        (31, 'zinc', 0.052),
        (31, 'molybdenum', 0.013),
        (31, 'tin', 0.012),
        (31, 'yttrium', 0.011),

        (32, 'chromium', 0.083),
        (32, 'manganese', 0.077),
        (32, 'germanium', 0.053),
        (32, 'niobium', 0.013),
        (32, 'yttrium', 0.011),
        (32, 'mercury', 0.008),

        (33, 'chromium', 0.054),
        (33, 'selenium', 0.042),
        (33, 'germanium', 0.035),
        (33, 'cadmium', 0.009),
        (33, 'molybdenum', 0.008),
        (33, 'ruthenium', 0.007),

        (34, 'selenium', 0.047),
        (34, 'manganese', 0.038),
        (34, 'vanadium', 0.022),
        (34, 'cadmium', 0.007),
        (34, 'niobium', 0.006),
        (34, 'ruthenium', 0.006),

        (35, 'zinc', 0.066),
        (35, 'selenium', 0.027),
        (35, 'arsenic', 0.023),
        (35, 'cadmium', 0.019),
        (35, 'tin', 0.016),
        (35, 'ruthenium', 0.015),

        (36, 'manganese', 0.083),
        (36, 'zinc', 0.054),
        (36, 'vanadium', 0.049),
        (36, 'ruthenium', 0.012),
        (36, 'tin', 0.012),
        (36, 'mercury', 0.009),

        (37, 'chromium', 0.051),
        (37, 'manganese', 0.046),
        (37, 'zinc', 0.031),
        (37, 'cadmium', 0.009),
        (37, 'molybdenum', 0.007),
        (37, 'yttrium', 0.007),

        (38, 'chromium', 0.054),
        (38, 'selenium', 0.042),
        (38, 'germanium', 0.035),
        (38, 'ruthenium', 0.007),
        (38, 'tin', 0.007),
        (38, 'tungsten', 0.007),

        (39,  'chromium', 0.054),
        (39,  'germanium', 0.035),
        (39,  'vanadium', 0.03),
        (39,  'cadmium', 0.009),
        (39,  'tellurium', 0.009),
        (39,  'niobium', 0.008),

        (40,  'manganese', 0.05),
        (40,  'selenium', 0.042),
        (40,  'vanadium', 0.03),
        (40,  'cadmium', 0.01),
        (40,  'tellurium', 0.009),
        (40,  'tungsten', 0.007),

        (41,  'chromium', 0.054),
        (41,  'manganese', 0.049),
        (41,  'germanium', 0.034),
        (41,  'tellurium', 0.009),
        (41,  'molybdenum', 0.008),
        (41,  'tungsten', 0.007),

        (42,  'manganese', 0.05),
        (42,  'selenium', 0.042),
        (42,  'vanadium', 0.03),
        (42,  'tellurium', 0.009),
        (42,  'tin', 0.007),
        (42,  'mercury', 0.005),

        (43,  'chromium', 0.055),
        (43,  'vanadium', 0.03),
        (43,  'arsenic', 0.016),
        (43,  'antimony', 0.008),
        (43,  'tin', 0.007),
        (43,  'tungsten', 0.007),

        (44,  'chromium', 0.053),
        (44,  'manganese', 0.049),
        (44,  'selenium', 0.041),
        (44,  'cadmium', 0.009),
        (44,  'niobium', 0.008),
        (44,  'antimony', 0.007),

        (45,  'chromium', 0.099),
        (45,  'zinc', 0.06),
        (45,  'vanadium', 0.054),
        (45,  'tin', 0.014),
        (45,  'tungsten', 0.012),
        (45,  'polonium', 0.006),

        (46,  'chromium', 0.054),
        (46,  'manganese', 0.049),
        (46,  'zinc', 0.032),
        (46,  'cadmium', 0.009),
        (46,  'molybdenum', 0.008),
        (46,  'ruthenium', 0.007),

        (47,  'chromium', 0.056),
        (47,  'vanadium', 0.031),
        (47,  'arsenic', 0.016),
        (47,  'cadmium', 0.01),
        (47,  'niobium', 0.009),
        (47,  'ruthenium', 0.008),

        (48,  'chromium', 0.057),
        (48,  'arsenic', 0.016),
        (48,  'zirconium', 0.015),
        (48,  'ruthenium', 0.008),
        (48,  'tin', 0.008),
        (48,  'tungsten', 0.007),

        (49,  'chromium', 0.054),
        (49,  'manganese', 0.049),
        (49,  'selenium', 0.041),
        (49,  'molybdenum', 0.008),
        (49,  'antimony', 0.007),
        (49,  'tin', 0.007),

        (50,  'chromium', 0.055),
        (50,  'manganese', 0.051),
        (50,  'zirconium', 0.014),
        (50,  'niobium', 0.008),
        (50,  'ruthenium', 0.008),
        (50,  'tin', 0.007),

        (51,  'chromium', 0.056),
        (51,  'zinc', 0.034),
        (51,  'zirconium', 0.014),
        (51,  'niobium', 0.009),
        (51,  'molybdenum', 0.008),
        (51,  'yttrium', 0.007),

        (52,  'manganese', 0.05),
        (52,  'zinc', 0.033),
        (52,  'vanadium', 0.03),
        (52,  'niobium', 0.008),
        (52,  'molybdenum', 0.008),
        (52,  'yttrium', 0.007),

        (53,  'chromium', 0.055),
        (53,  'manganese', 0.05),
        (53,  'germanium', 0.035),
        (53,  'tellurium', 0.009),
        (53,  'molybdenum', 0.008),
        (53,  'mercury', 0.005),

        (54,  'manganese', 0.051),
        (54,  'germanium', 0.035),
        (54,  'vanadium', 0.03),
        (54,  'antimony', 0.008),
        (54,  'tin', 0.007),
        (54,  'mercury', 0.005),

        (55,  'chromium', 0.054),
        (55,  'selenium', 0.042),
        (55,  'germanium', 0.035),
        (55,  'niobium', 0.008),
        (55,  'antimony', 0.007),
        (55,  'mercury', 0.005),

        (56,  'chromium', 0.055),
        (56,  'selenium', 0.042),
        (56,  'zinc', 0.033),
        (56,  'cadmium', 0.01),
        (56,  'tin', 0.007),
        (56,  'yttrium', 0.007),

        (57,  'chromium', 0.054),
        (57,  'selenium', 0.042),
        (57,  'germanium', 0.035),
        (57,  'molybdenum', 0.008),
        (57,  'tin', 0.007),
        (57,  'technetium', 0.004),

        (58,  'chromium', 0.055),
        (58,  'germanium', 0.035),
        (58,  'vanadium', 0.03),
        (58,  'ruthenium', 0.008),
        (58,  'tin', 0.007),
        (58,  'tungsten', 0.007),

        (59,  'chromium', 0.159),
        (59,  'manganese', 0.146),
        (59,  'niobium', 0.024),
        (59,  'molybdenum', 0.023),
        (59,  'germanium', 0.017),
        (59,  'antimony', 0.013),

        (60,  'selenium', 0.043),
        (60,  'germanium', 0.036),
        (60,  'vanadium', 0.03),
        (60,  'cadmium', 0.01),
        (60,  'yttrium', 0.007),
        (60,  'tungsten', 0.007),

        (61,  'germanium', 0.037),
        (61,  'vanadium', 0.031),
        (61,  'arsenic', 0.016),
        (61,  'ruthenium', 0.008),
        (61,  'tin', 0.008),
        (61,  'tungsten', 0.007),

        (62,  'selenium', 0.043),
        (62,  'germanium', 0.035),
        (62,  'zinc', 0.034),
        (62,  'niobium', 0.008),
        (62,  'yttrium', 0.007),
        (62,  'tin', 0.007),

        (63,  'chromium', 0.056),
        (63,  'germanium', 0.035),
        (63,  'vanadium', 0.03),
        (63,  'yttrium', 0.007),
        (63,  'tin', 0.007),
        (63,  'tungsten', 0.007),

        (64,  'selenium', 0.044),
        (64,  'zinc', 0.034),
        (64,  'zirconium', 0.015),
        (64,  'cadmium', 0.01),
        (64,  'tungsten', 0.007),
        (64,  'polonium', 0.003),

        (65,  'chromium', 0.054),
        (65,  'manganese', 0.05),
        (65,  'vanadium', 0.029),
        (65,  'tellurium', 0.009),
        (65,  'tin', 0.007),
        (65,  'tungsten', 0.007),

        (66,  'chromium', 0.054),
        (66,  'selenium', 0.042),
        (66,  'zinc', 0.033),
        (66,  'molybdenum', 0.008),
        (66,  'ruthenium', 0.007),
        (66,  'tin', 0.007),

        (67,  'chromium', 0.054),
        (67,  'manganese', 0.049),
        (67,  'zinc', 0.033),
        (67,  'cadmium', 0.009),
        (67,  'tellurium', 0.009),
        (67,  'niobium', 0.008)
    ]

    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'rawdepletables')
        try:
            self.db = sqlite3.connect(path)
            cursor = self.db.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS
                            hotspots(id INTEGER PRIMARY KEY, name TEXT, planet TEXT, gravity REAL, distance_to_arrival INTEGER, type TEXT, confirmed INTEGER DEFAULT 0, last_visit INTEGER DEFAULT 0)
                            ''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS
                            concentrations(id INTEGER PRIMARY KEY, hotspotid INTEGER SECONDARY KEY, resource TEXT, concentration REAL)
                            ''')
            for hotspot in EDRRawDepletables.HOTSPOTS:
                check = cursor.execute("SELECT name, planet from hotspots where name=? and planet=?", (hotspot[0:2]))
                test = check.fetchone()
                if not test:
                    cursor.execute('insert into hotspots(name, planet, gravity, distance_to_arrival, type, confirmed) values (?,?,?,?,?,?)', hotspot)
            for concentration in EDRRawDepletables.CONCENTRATIONS:
                check = cursor.execute("SELECT hotspotid from concentrations where hotspotid=?", (concentration[0:1]))
                if not check.fetchone():
                    cursor.execute('insert into concentrations(hotspotid, resource, concentration) values (?,?,?)', concentration)
            self.db.commit()
        except:
            EDR_LOG.log(u"Couldn't open/create the depletables database", "ERROR")
            self.db = None
    
    def visit(self, poi_name):
        if not poi_name:
            return
        poi = EDRRawDepletables.POI_LUT.get(poi_name.lower(), None)
        if poi:
            self.__visit(poi["system"], poi["planet"])

    def __visit(self, system, planet):
        if self.db is None:
            return
        try:
            now = EDTime.py_epoch_now()
            self.db.execute('UPDATE hotspots SET last_visit= CASE WHEN last_visit < ? THEN (?) ELSE (last_visit) END WHERE name=? and planet=?', (self.__replenished_margin(), now, system, planet))
            self.db.commit()
        except sqlite3.IntegrityError:
            pass

    def __replenished_margin(self):
        margin = 1*60*60
        return EDTime.py_epoch_now() - (14*24*60*60 + margin)

    def hotspots(self, resource_name):
        if self.db is None:
            return
        check = self.db.execute("SELECT id from hotspots limit 1")
        if not check.fetchone():
            return False
        cursor = self.db.execute('SELECT name, planet, gravity, distance_to_arrival, type, last_visit, concentration FROM hotspots INNER JOIN concentrations ON hotspots.id = concentrations.hotspotid WHERE resource=? and last_visit<? and confirmed>=0', (resource_name.lower(), self.__replenished_margin()))
        return cursor.fetchall()
