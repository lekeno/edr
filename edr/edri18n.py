#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import

import gettext
import os

import utils2to3


CONTEXT_SEPARATOR = u"|"
L10N_DIR = utils2to3.abspathmaker(__file__, 'l10n')
language = None
translate = gettext.translation('edr', L10N_DIR, fallback=True, codeset="utf-8")

def set_language(lang):
    global language, translate
    language = lang
    if language:
        translate = gettext.translation('edr', L10N_DIR, fallback=True, languages=[language], codeset="utf-8")
    else:
        translate = gettext.translation('edr', L10N_DIR, fallback=True, codeset="utf-8")

def ugettext(message):
    return translate.ugettext(message)

def pgettext(contextual_message):
    global translate
    result = translate.ugettext(contextual_message)
    if CONTEXT_SEPARATOR in result:
        # Translation not found
        result = contextual_message.split(u"|")[1]
    return result

def edrgettext(message_maybe_localized):
    global language
    try:
        return message_maybe_localized[language]
    except:
        if "default" in message_maybe_localized:
            return message_maybe_localized["default"]
        else:
            return message_maybe_localized

_ = ugettext
_c = pgettext
_edr= edrgettext