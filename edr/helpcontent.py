#!/usr/bin/env python
# coding=utf-8

import os
import json

import utils2to3

def _(message): return message

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
                _(u" - !help central: dispatch a request to EDR central: general, police, fuel, repair"),
                _(u" - !help enforcers: features for enforcers / bounty hunters"),
                _(u" - !help powerplay: features for commanders pledged to a power"),
                _(u" - !help cmdrdex: personalizing EDR's commanders database"),
                _(u" - !help sqdrdex: tag other commanders as ally or enemy of your squadron"),
                _(u" - !help nearby: commands to find services near you or a specific system, e.g. interstellar factors"),
                _(u" - !help search: find the best spots to obtain engineering resources or exobiology"),
                _(u" - !help ship: find out where you've parked your ships, evaluate your build, find a fleet carrier parking slot"),
                _(u" - !help odyssey: evaluate your storage of materials, know if a material is useful or not"),
                _(u" - !help config: configuration options"),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "about": {
            "header": _(u"About EDR"),
            "details": [
                _(u"ED Recon is a third party plugin for Elite Dangerous. Its purpose is to provide insights about outlaws to traders, explorers, and bounty hunters."),
                _(u" - EDR is in beta, is developed by LeKeno, and uses a customized version of Ian Norton's EDMCOverlay for the overlay."),
                _(u" - It is TOS compliant because it uses Elite Dangerous's player journal which has been designed for third party consumption."),
                _(u" - EDR is free to use but you can support EDR's development and server costs at https://patreon.com/lekeno"),
                _(u" - Got feedback or questions? Please file bugs, feature requests or questions at https://github.com/lekeno/edr/issues/"),
                u"⚶",
                _(u"Translations (see https://github.com/lekeno/edr/issues/135)."),
                _(u" - Contributions by : Juniper Nomi'Tar [UGC], Tomski [bbFA], Jason Hill and MonkasteR"),
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
                _(u" - reporting of traffic, outlaws, crimes, and fights."),
                _(u" - reporting scans of commanders with legal status and bounties."),
                _(u" - reporting and getting insights about powerplay enemies."),
                u"⚶",
                _(u"These insights will also help other EDR users so consider applying for an EDR account at https://edrecon.com/account"),
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
                _(u" - '!distance system_name', '!d system_name': to display the distance from your position to 'system_name'."),
                _(u" - '!distance A > B', '!d A > B': to display the distance from 'A' to 'B'."),
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
                _(u" - Point at, or salute another player with the emote gestures to show their EDR and Inara profile."),
                _(u"These commands will show the following information:"),
                _(u" - EDR alignment: outlaw, ambiguous, lawful with grades, e.g. outlaw ++++."),
                _(u" - User tags: [!12, ?1, +0], i.e. 12 users marked that commander as an outlaw, 1 as neutral, 0 as enforcer."),
                _(u" - Inara info: squadron and role if any (sometimes superseded by EDR)."),
                _(u" - Personal tags/info from your CmdrDex if any (see !help cmdrdex)."),
                _(u" - Legal record: # of clean vs. wanted scans, max and latest known bounties"),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "central": {
            "header": _(u"EDR Central"),
            "details": [
                _(u"You can dispatch a request to EDR Central's restricted discord channels."),
                _(u"The request will automatically include your status (e.g. cmdr name, ship, etc.) and other relevant information."),
                _(u" - '!edr your message.' to dispatch a generic message."),
                _(u" - '!911 your message.' to dispatch a police request."),
                _(u" - '!fuel your message.' to dispatch a fuel request."),
                _(u" - '!repair your message.' to dispatch a repair request."),
                _(u"If the message is successfully sent, you will see a confirmation with a codeword."),
                _(u"If anyone is available, you should receive a friend request or a direct message."),
                _(u"Identify trustworthy commanders by asking them for the codeword and checking their profile via EDR."),
                _(u"Note: abusing this feature will result in revoking your access to EDR features."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "enforcers": {
            "header": _(u"Enforcers"),
            "details": [
                _(u"Chat commands for enforcers:"),
                _(u" - '!outlaws': to display a list of most recently sighted outlaws and their locations."),
                _(u" - '?outlaws [on|off]': to enable/disable realtime alerts for sighted outlaws."),
                _(u" - '?outlaws cr 10000': to configure a minimal bounty of 10k cr for the realtime alerts."),
                _(u" - '?outlaws ly 150': to configure a maximal distance of 150 ly for the realtime alerts."),
                _(u" - '?outlaws [cr|ly] -': to remove the [minimal bounty|maximal distance] for the realtime alerts."),
                _(u" - '!where cmdr_name': to display the last sighting of the cmdr called cmdr_name provided that EDR considers them an outlaw."),
                _(u" - '#!' or '#?' or '#+': to mark a cmdr as an outlaw, neutral or enforcer (see !help cmdrdex for more details)."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "powerplay": {
            "header": _(u"Powerplay"),
            "details": [
                _(u"When pledged to a power, your EDR module will also report powerplay enemies."),
                _(u"Sitreps will also show any sighted enemies in a dedicated section."),
                _(u"Chat commands for commanders who have been loyal to their allegiance for more than 30 days:"),
                _(u" - '!enemies': to display a list of most recently sighted enemies and their locations."),
                _(u" - '?enemies [on|off]': to enable/disable realtime alerts for sighted enemies."),
                _(u" - '?enemies cr 10000': to configure a minimal bounty of 10k cr for the realtime alerts."),
                _(u" - '?enemies ly 150': to configure a maximal distance of 150 ly for the realtime alerts."),
                _(u" - '?enemies [cr|ly] -': to remove the [minimal bounty|maximal distance] for the realtime alerts."),
                _(u" - '!where cmdr_name': to display the last sighting of cmdr_name provided that they are an enemy or outlaw."),
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
        "sqdrdex": {
            "header": _(u"Tagging allies and enemies of your squadron"),
            "details": [
                _(u"The Squadron Dex allows you to tag other commanders as allies or enemies of your squadron."),
                _(u"To use this feature, you will need to be an active member of a squadron on https://inara.cz."),
                _(u"Read access: Co-pilot and above. Write access: wingman and above. Updating: same or higher rank."),
                _(u"Updating/Deleting existing entries: same or higher rank than the member who created it."),
                u"⚶",
                _(u"Ally and Enemy tags:"),
                _(u"Send !help cmdrdex for general usage info."),
                _(u" - '#ally' or '#s+': to tag a commander as an ally."),
                _(u" - '#enemy' or '#s!': to tag a commander as an enemy."),
                _(u" - '-#ally' or '-#s+': to remove an ally tag off a commander."),
                _(u" - '-#enemy' or '-#s!': to remove an enemy tag off a commander."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "nearby": {
            "header": _(u"Finding things around you or a specified system Ⅰ"),
            "details": [
                _(u" - '!if' or '!if Lave' to find an Interstellar Factors near your position or Lave."),
                _(u" - '!raw' or '!raw Lave' to find a Raw Material Trader near your position or Lave"),
                _(u" - '!encoded', !enc' or '!enc Lave' to find an Encoded Data Trader near your position or Lave"),
                _(u" - '!manufactured', '!man' or '!man Lave' to find a Manufactured Material Trader near your position or Lave"),
                _(u" - '!staging' or '!staging Lave' to find a good staging station near your position or Lave, i.e. large pads, shipyard, outfitting, repair/rearm/refuel."),
                _(u" - '!htb', '!humantechbroker' or '!htb Lave' to find a Human Tech Broker near your position or Lave"),
                _(u" - '!gtb', '!guardiantechbroker' or '!gtb Lave' to find a Guardian Tech Broker near your position or Lave"),
                _(u" - '!nav 12.3 -4.5', '!nav set' or '!nav off' to obtain planetary guidance for getting to a specific location"),
                _(u" - '!nav clear', '!nav reset', '!nav next', '!nav previous' to clear or reset custom POIs, or select the next/previous custom POI on a planet"),
                _(u" - '!offbeat', '!offbeat Lave' to find a station that hasn't been recently visited near your position or Lave"),
                u"⚶",
                _(u"Send !help nearby2 to see other nearby features. Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "nearby2": {
            "header": _(u"Finding things around you or a specified system Ⅱ"),
            "details": [
                _(u" - '!rrrfc', '!rrrfc Lave < 10' to find a fleet carrier with repair/rearm/refuel near your position or within 10 LY of Lave"),
                _(u" - '!rrr', '!rrr Lave < 10' to find a station with repair/rearm/refuel near your position or within 10 LY of Lave"),
                _(u" - '!fc J6B', '!fc Recon' to display information about a local fleet carrier with a callsign or name that contains J6B or Recon"),
                _(u" - '!station Jameson' to display information about a local station/outpost/... with a name that contains Jameson"),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "search": {
            "header": _(u"Find the best spots for resources and exobiology"),
            "details": [
                _(u" - '!search thing' where thing is either the full name or an abbreviation, e.g. !search cadmium"),
                _(u" - '!search thing @system' to specify the system to search around, e.g. !search cadmium @deciat"),
                _(u" - Abbreviations consist of the first three letters of a one-word resource, or the first letters of each words separated by a space:"),
                _(u" - 'cad' for cadmium, 'a e c d' for abnormal compact emission data."),
                _(u" - Use the command with a few letters to see the supported keywords that contain these letters, e.g. '!search strat"),
                _(u" - Some manufactured materials may not always return a result. Use the hints and Elite's galaxy map to find a good spot."),
                _(u" - Finally, when jumping into a system, EDR will tell you if it has the right conditions for specific materials, e.g. Imperial Shielding (USS-HGE, +++++)."),
                _(u" - The more '+', the higher the chances."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "ship": {
            "header": _(u"Find where you parked your ship, evaluate your build"),
            "details": [
                _(u" - '!ship name_or_type' where name_or_type is either a ship name or type."),
                _(u" - '!ship fdl' will show where your Fer-de-Lance ships are parked."),
                _(u" - '!ship In Front of Things' will show where your ship(s) named 'In Front of Things' are."),
                _(u" - '!eval power' to get an assessment of your power priorities."),
                u"⚶",
                _(u" - '!parking', '!parking deciat', '!parking deciat #1' to check for fleet carrier parking slots in the current system, Deciat, or the second closest system to Deciat."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "config": {
            "header": _(u"Configuration options"),
            "details": [
                _(u"EDR offers the following configuration options:"),
                _(u" - !crimes [off|on]: to disable/enable crime and fight reporting, e.g. '!crimes off' before an agreed upon duel."),
                _(u" - !audiocue [on|off|loud|soft] to control the audio cues, e.g. '!audiocue soft' for soft cues."),
                _(u" - !overlay [on|off|] to enable/disable or verify the overlay, e.g. '!overlay' to check if it is enabled/working."),
                _(u" - check the instructions in config/igm_config.v8.ini to customize the layout and timeouts."),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "odyssey": {
            "header": _(u"Odyssey"),
            "details": [
                _(u"EDR offers the following features to help you make sense of Odyssey materials, engineers and exobiology:"),
                _(u" - !eval [locker|backpack]: to evaluate the usefulness of materials in your ship locker or backpack, e.g. '!eval locker'. Useful when selling stuff at the bar, or via your fleet carrier."),
                _(u" - !eval [name of the material] to evaluate the usefulness of a specific material, e.g. '!eval surveillance equipment'. Useful to assess a reward before accepting a mission."),
                _(u" - Point at materials while on foot with the emote gesture to get EDR to identify it and provide info about its usefulness."),
                _(u" - !eval [bar|bar demand] to evaluate the items on sale (or in demand) at the last visited bar on a fleet carrier, e.g. '!eval bar demand'. Useful to know which items to buy / sale."),
                _(u" - Visit the bar on a fleet carrier to get a list of most useful items on sale, or least useful items in demand."),
                _(u" - Exobiology hints and progress tracking when targeting a planet, being in its orbit or by sending the '!biology' command (e.g. '!biology 1 A'"),
                u"⚶",
                _(u"Send !clear in chat to clear everything on the overlay.")
            ]
        }
    }

    def __init__(self, help_file=None):
        if help_file:
            self.content = json.loads(open(utils2to3.abspathmaker(__file__, help_file)).read())
        else:
            self.content = HelpContent.DEFAULT_CONTENT

    def get(self, category):
        if category in self.content.keys():
            return self.content[category]
        return None

del _