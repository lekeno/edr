#!/usr/bin/env python
# coding=utf-8

import gettext
import os
from config import config

l10ndir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'l10n')
# TODO find a way to update when preferences have changed
translate = gettext.translation('edr', l10ndir, fallback=True, languages=[config.get('language')], codeset="utf-8")
_ = translate.ugettext

CONTEXT_SEPARATOR = u"|"

def pgettext(contextual_message):
    result = translate.ugettext(contextual_message)
    if CONTEXT_SEPARATOR in result:
        # Translation not found
        result = contextual_message.split(u"|")[1]
    return result

_c = pgettext
