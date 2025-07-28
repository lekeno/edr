#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import

import gettext
# import os # 'os' imported but unused Flake8(F401)
import sys

import l10n  # Importing localization module
import os
from edrlog import EDR_LOG

# Constants
CONTEXT_SEPARATOR = u"|"  # Separator used for contextual message
L10N_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'l10n')  # Directory for localization files
LANG_LIST = ["fr", "it", "de"]  # List of supported languages

# Logger
  # Creating an instance of EDRLog for logging

# Global variables
language = None
translate = gettext.translation('edr', L10N_DIR, fallback=True)  # Translation object
pref_langs = None


def _get_sys_lang():
    """
    Attempt to retrieve the system language preference and select the first preferred language if available.
    Return the selected language or None if no language is selected.
    """
    try:
        # Attempting to get preferred languages from l10n module
        pref_langs = list(l10n.Locale.preferred_languages())
        # Select the first preferred language if it is supported by the list of supported languages.
        # If the preferred language is supported, extract only the primary language from the string;
        # otherwise, set select_lang to None.
        if pref_langs[0].split("-")[0] in LANG_LIST:
            # Extract the primary language from the first preferred language
            select_lang = pref_langs[0].split("-")[0]
        else:
            # If the first preferred language is not supported, set select_lang to None
            select_lang = None
    except AttributeError as e:
        # Handling AttributeError when attempting to retrieve preferred languages
        EDR_LOG.log("AttributeError occurred: {}.".format(e), "ERROR")
        select_lang = None
    except (IndexError, TypeError, KeyError) as e:
        # Handling specific exceptions
        EDR_LOG.log(u"Error occurred: {}.".format(e), "ERROR")
        select_lang = None
    except Exception as e:
        # Handling other exceptions
        EDR_LOG.log(u"An unexpected error occurred: {}.".format(e), "ERROR")
        select_lang = None
    finally:
        # Logging the acceptance of the system language for translation
        if select_lang is not None:
            EDR_LOG.log(u"The system language ({}) is accepted for translation.".format(select_lang), "INFO")
        else:
            EDR_LOG.log(u"The system language is not accepted for translation, English will be used.", "INFO")

    return select_lang


def set_language(lang):
    """
    Set the language for translation.

    Args:
        lang (str): The language code to set.

    Returns:
        None
    """
    global language, translate

    # Store the current language preference obtained from the system
    _sys_lang = _get_sys_lang()

    # Set the language based on the input parameter or the system preference
    if lang:
        # Set custom language if provided
        language = lang
        translate = gettext.translation('edr', L10N_DIR, fallback=True, languages=[language])
        EDR_LOG.log(u"The EDMC language parameter is set to custom: lang {}.".format(language), "INFO")
    elif _sys_lang:
        # Set default language if available
        language = _sys_lang
        translate = gettext.translation('edr', L10N_DIR, fallback=True, languages=[language])
        EDR_LOG.log(u"The EDMC language parameter is set to default.", "INFO")
    else:
        # Set fallback to English if neither custom nor system language available
        translate = gettext.translation('edr', L10N_DIR, fallback=True)
        EDR_LOG.log(u"Failed to set EDMC language parameter, falling back to English.", "INFO")


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
