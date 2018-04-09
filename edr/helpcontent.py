#!/usr/bin/env python
# coding=utf-8

import os
import json
from edri18n import _, _c

class HelpContent(object):

    DEFAULT_CONTENT = {
        "": {
            "header": _(u"Help sections"),
            "details": [
                _(u" - !help about: what is EDR, who is behind it, etc"),
                _(u" - !help basics: getting started with EDR"),
                _(u" - !help account: doing more with an EDR account (free)"),
                _(u" - !help system: star system related features"),
                _(u" - !help cmdr: commander related features"),
                _(u" - !help enforcers: features for enforcers / bounty hunters"),
                _(u" - !help cmdrdex: personalizing EDR's commanders database"),
                _(u" - !help config: configuration options"),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "about": {
            "header": _(u"About EDR"),
            "details": [
                _(u"ED Recon is a third party plugin for Elite Dangerous. Its purpose is to provide insights about outlaws to traders, explorers, and bounty hunters."),
                _(u" - EDR is in beta, is developed by LeKeno from Cobra Kai, and uses a customized version of Ian Norton's EDMCOverlay for the overlay."),
                _(u" - It is TOS compliant because it uses Elite Dangerous's player journal which has been designed for third party consumption."),
                _(u" - EDR is free to use but you can support EDR's development and server costs at https://patreon.com/lekeno"),
                _(u" - Got feedback or questions? Please file bugs, feature requests or questions at https://github.com/lekeno/edr/issues/"),
                u"⚶",
                _(u"Translations (see https://github.com/lekeno/edr/issues/135)."),
                _(u" - Contributions by : Juniper Nomi'Tar [UGC], Tomski [bbFA]"),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "basics": {
            "header": _(u"Getting started with EDR"),
            "details": [
                _(u"EDR will proactively show various insights as you fly around and scan other commanders:"),
                _(u" - A summary of recent activity as you jump into a system."),
                _(u" - EDR and Inara profile for known outlaws as they are sighted (e.g. scanned) or detected (e.g. chat)."), 
                u"⚶",
                _(u"You can ask EDR for insights by issuing various commands via the in-game chat:"),
                _(u" - '!sitrep Lave' to find out if Lave has seen some recent activity."),
                _(u" - '!notams' to find out which systems are considered hotspots."),
                _(u"Learn more with '!help system' and '!help cmdr'"),
                u"⚶",
                _(u"You can also customize EDR to your needs with the cmdrdex features, send '!help cmdrdex' to learn more."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "account": {
            "header": _(u"EDR account"),
            "details": [
                _(u"While EDR provides useful information without any credentials, it has a lot more to offer with an account."),
                u"⚶",
                _(u"Important: with an account EDR may report your location to the backend. However, this information will not be shown to other EDR users."),
                _(u"In the future, this might be used to help enforcers join forces or for check and balance reasons, e.g. reporting outlaw EDR users."),
                u"⚶",
                _(u"An EDR account is free and unlocks all of EDR's features. For instance:"),
                _(u" - personalizing / augmenting EDR's commanders database."),
                _(u" - reporting of traffic, outlaws and crimes."),
                _(u" - reporting scans of commanders with legal status and bounties."),
                u"⚶",
                _(u"These insights will also help other EDR users so consider applying for an EDR account at https://lekeno.github.io/"),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "system": {
            "header": _(u"Star system related features"),
            "details": [
                _(u"When jumping to a system, EDR will show a sitrep for the system: active notices, i.e. NOTAM, summary of recent activity, etc."),
                _(u"Send the following command via the in-game chat to get intel about recent activity or specific systems:"),
                _(u" - '!sitreps': to display a list of star systems with sitreps."),
                _(u" - '!sitrep': to display the sitrep for the current system."),
                _(u" - '!sitrep system_name': to display the sitrep for the star system called system_name."),
                _(u" - '!notams': to display a list of star systems with active notices, i.e. Notice To Air Men."),
                _(u" - '!notam system_name': to display any active notice the star system called system_name."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "cmdr": {
            "header": _(u"Commander related features"),
            "details": [
                _(u"Use the following chat commands to lookup a commander's profile:"),
                _(u" - 'o7': direct message a commander with a salute emoji to see their EDR and Inara profile."),
                _(u" - '!who cmdr_name': to see cmdr_name's EDR and Inara profile."),
                _(u"These commands will show the following information:"),
                _(u" - EDR alignment: wanted, neutral, enforcer with grades, e.g. wanted ++++."),
                _(u" - User tags: [!12, ?1, +0], i.e. 12 users marked that commander as an outlaw, 1 as neutral, 0 as enforcer."),
                _(u" - Inara info: squadron and role if any (sometimes superseded by EDR)."),
                _(u" - Personal tags/info from your CmdrDex if any (see !help cmdrdex)."),
                _(u" - Legal record: # of clean vs. wanted scans, max and latest known bounties"),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "enforcers": {
            "header": _(u"Enforcers"),
            "details": [
                _(u"Chat commands for enforcers:"),
                _(u" - '!outlaws': to display a list of most recently sighted outlaws and their locations."),
                _(u" - '!where cmdr_name': to display the last sighting of the cmdr called cmdr_name provided that EDR considers them an outlaw."),
                _(u" - '#!' or '#?' or '#+': to mark a cmdr as an outlaw, neutral or enforcer (see !help cmdrdex for more details)."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "cmdrdex": {
            "header": _(u"Personalizing EDR's commanders database"),
            "details": [
                _(u"The CmdrDex allows you to customize EDR and helps EDR users make informed guesses about other commanders."),
                _(u"Your CmdrDex is personal, EDR will only show aggregated stats for the alignment tags."),
                _(u"General rules for the cmdrdex chat commands:"),
                _(u" - '#something' or '#something cmdr_name': to tag a contact or cmdr_name with the 'something' tag, e.g. #pirate jack sparrow."),
                _(u" - '-#something' or '-#something cmdr_name': to remove the 'something' tag from a contact or cmdr_name."),
                _(u" - '-#' or '-# cmdr_name': to remove a contact or cmdr_name from your cmdrdex."),
                u"⚶",
                _(u"EDR pre-defined tags:"),
                _(u" - 'outlaw' or '!': for cmdrs who either attacked you or someone despite being clean and non pledged to an enemy power."),
                _(u" - 'enforcer' or '+': for cmdrs who are on the good side of the law and hunt outlaws."),
                _(u" - 'neutral' or '?': if you disagree with EDR's classification and want to suppress its warning, or if a commander just seems to go about their own business."),
                _(u" - 'friend' or '=': to tag like-minded cmdrs, EDR may infer a social graph from these in the future."),
                u"⚶",
                _(u"Attaching a note:"),
                _(u" - '@# <memo>' or '@# cmdr_name memo=something': to attach a note to a contact or cmdr_name, e.g. '@# friendly trader."),
                _(u" - '-@#' or '-@# cmdr_name': to remove the custom note from a contact or cmdr_name."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "config": {
            "header": _(u"Configuration options"),
            "details": [
                _(u"EDR offers the following configuration options:"),
                _(u" - !crimes [off|on]: to disable/enable crime reporting, e.g. '!crimes off' before an agreed upon duel."),
                _(u" - !audiocue [on|off|loud|soft] to control the audio cues, e.g. '!audiocue soft' for soft cues."),
                _(u" - !overlay [on|off|] to enable/disable or verify the overlay, e.g. '!overlay' to check if it is enabled/working."),
                _(u" - check the instructions in config/igm_config.v2.ini to customize the layout and timeouts."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        }
    }

    def __init__(self, help_file=None):
        if help_file:
            self.content = json.loads(open(os.path.join(
                os.path.abspath(os.path.dirname(__file__)), help_file)).read())
        else:
            self.content = HelpContent.DEFAULT_CONTENT

    def get(self, category):
        if category in self.content.keys():
            return self.content[category]
        return None