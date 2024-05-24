#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import

import gettext
# import os # 'os' imported but unused Flake8(F401)
import sys

import l10n  # Importing localization module
import utils2to3
from edrlog import EDRLog  # Importing EDRLog module for logging

# Constants
CONTEXT_SEPARATOR = u"|"  # Separator used for contextual message
L10N_DIR = utils2to3.abspathmaker(__file__, 'l10n')  # Directory for localization files
LANG_LIST = ["fr", "it", "de"]  # List of supported languages

# Logger
EDRLOG = EDRLog()  # Creating an instance of EDRLog for logging

# Global variables
language = None
translate = gettext.translation('edr', L10N_DIR, fallback=True)  # Translation object

try:
    # Attempting to get preferred languages from l10n module
    pref_langs = list(l10n.Locale.preferred_languages())
    # Selecting the first preferred language if available and supported
    select_lang = pref_langs[0][:-3] if pref_langs and pref_langs[0][:-3] in LANG_LIST else None
except AttributeError as e:
    # Handling error when the attribute preferred_languages is not available
    EDRLOG.log(u"AttributeError: {}".format(e), "WARNING")
    select_lang = None


def set_language(lang):  # Function to set the language for translation
    global language, translate
    language = lang
    if language:
        translate = gettext.translation('edr', L10N_DIR, fallback=True, languages=[language])
        EDRLOG.log(u"pass 1: lang {}".format(language), "INFO")  # Logging language selection
    elif select_lang:
        language = select_lang
        translate = gettext.translation('edr', L10N_DIR, fallback=True, languages=[language])
        EDRLOG.log(u"pass 2: lang {}".format(language), "INFO")  # Logging language selection
    else:
        translate = gettext.translation('edr', L10N_DIR, fallback=True)
        EDRLOG.log(u"Fail: lang en", "INFO")  # Logging failure to select language


def ugettext(message):  # Function to translate a message
    if sys.version_info.major == 2:
        return translate.ugettext(message)
    else:
        return translate.gettext(message)


def pgettext(contextual_message):  # Function to translate a contextual message
    global translate
    result = None
    if sys.version_info.major == 2:
        result = translate.ugettext(contextual_message)
    else:
        result = translate.gettext(contextual_message)
    if CONTEXT_SEPARATOR in result:
        # Translation not found, returning the default message
        result = contextual_message.split(u"|")[1]
    return result


def edrgettext(message_maybe_localized):  # Function to get a localized message
    global language
    try:
        return message_maybe_localized[language]
    except KeyError:
        if "default" in message_maybe_localized:
            return message_maybe_localized["default"]
        else:
            return message_maybe_localized


_ = ugettext  # Alias for ugettext
_c = pgettext  # Alias for pgettext
_edr = edrgettext  # Alias for edrgettext
