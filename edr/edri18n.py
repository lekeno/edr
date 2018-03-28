import gettext
import os

l10ndir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'l10n')
translate = gettext.translation('edr', l10ndir, fallback=True, languages=['fr'])
print translate
_ = translate.ugettext

CONTEXT_SEPARATOR = u"|"

def pgettext(contextual_message):
    result = translate.gettext(contextual_message)
    if CONTEXT_SEPARATOR in result:
        # Translation not found
        result = contextual_message.split("|")[1]
    return result

_c = pgettext
