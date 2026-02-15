import gettext
import os

import l10n
from .edrlog import EDR_LOG  # EDR_INTERNAL

# Constants
CONTEXT_SEPARATOR = "|"
L10N_DIR = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')), 'l10n')
LANG_LIST = ["fr", "it", "de"]

# Global variables
LANGUAGE = None
TRANSLATE = gettext.translation('edr', L10N_DIR, fallback=True)


def _get_sys_lang():
    """
    Attempt to retrieve the system language preference and select the first preferred language if available.

    Returns:
        str: The selected language code or None if no matching language is available.
    """
    select_lang = None
    try:
        # Attempting to get preferred languages from l10n module
        pref_langs = list(l10n.Locale.preferred_languages() or [])
        if pref_langs:
            primary_lang = pref_langs[0].split("-")[0]
            select_lang = primary_lang if primary_lang in LANG_LIST else None

    except Exception:
        EDR_LOG.exception("Error during language selection.")
        select_lang = None

    finally:
        if select_lang is not None:
            EDR_LOG.info(f"The system language ({select_lang}) is accepted for translation.")
        else:
            EDR_LOG.info("The system language is not accepted for translation, English will be used.")

    return select_lang


def set_language(lang):
    """
    Set the language for translation.

    Args:
        lang (str): The language code to set.
    """
    global LANGUAGE, TRANSLATE

    _sys_lang = _get_sys_lang()

    if lang:
        LANGUAGE = lang
        TRANSLATE = gettext.translation('edr', L10N_DIR, fallback=True, languages=[LANGUAGE])
        EDR_LOG.info(f"The EDMC language parameter is set to custom: lang {LANGUAGE}.")
    elif _sys_lang:
        LANGUAGE = _sys_lang
        TRANSLATE = gettext.translation('edr', L10N_DIR, fallback=True, languages=[LANGUAGE])
        EDR_LOG.info("The EDMC language parameter is set to default.")
    else:
        TRANSLATE = gettext.translation('edr', L10N_DIR, fallback=True)
        LANGUAGE = 'en'
        EDR_LOG.info("Failed to set EDMC language parameter, falling back to English.")


def ugettext(message):
    """
    Translate a message.

    Args:
        message (str): The message to translate.

    Returns:
        str: The translated message.
    """
    return TRANSLATE.gettext(message)


def pgettext(contextual_message):
    """
    Translate a contextual message.

    Args:
        contextual_message (str): The contextual message (context|message).

    Returns:
        str: The translated message.
    """
    result = TRANSLATE.gettext(contextual_message)
    if CONTEXT_SEPARATOR in result:
        # Translation not found, returning the default message
        result = contextual_message.split(CONTEXT_SEPARATOR)[1]
    return result


def edrgettext(message_maybe_localized):
    """
    Get a localized message from a dictionary or string.

    Args:
        message_maybe_localized (str|dict): The message or dictionary of messages.

    Returns:
        str: The localized message.
    """
    global LANGUAGE

    if isinstance(message_maybe_localized, str):
        return message_maybe_localized

    if not isinstance(message_maybe_localized, dict):
        return str(message_maybe_localized) if message_maybe_localized else ""

    try:
        return message_maybe_localized[LANGUAGE]
    except KeyError:
        if "default" in message_maybe_localized:
            return message_maybe_localized["default"]
        elif "en" in message_maybe_localized:
            return message_maybe_localized["en"]

        return next(iter(message_maybe_localized.values())) if message_maybe_localized else ""


# Aliases
_ = ugettext
_c = pgettext
_edr = edrgettext
