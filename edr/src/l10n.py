class Translations:
    def gettext(self, text): return text
def Translations_fallback(*args, **kwargs): return Translations()
class Locale:
    @staticmethod
    def preferred_languages(): return ["en"]
