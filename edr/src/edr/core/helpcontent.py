import os
import json
from edr.utils.edrpath import plugin_root

def _(message): return message

class HelpContent:

    DEFAULT_CONTENT = {
        "": {
            "header": _("Help sections"),
            "details": [
                _(" - !help about: what is EDR, who is behind it, etc"),
                _(" - !help basics: getting started with EDR"),
                _(" - !help account: doing more with an EDR account (free)"),
                _(" - !help system: star system related features"),
                _(" - !help cmdr: commander related features"),
                _(" - !help central: dispatch a request to EDR central: general, police, fuel, repair"),
                _(" - !help enforcers: features for enforcers / bounty hunters"),
                _(" - !help powerplay: features for commanders pledged to a power"),
                _(" - !help cmdrdex: personalizing EDR's commanders database"),
                _(" - !help sqdrdex: tag other commanders as ally or enemy of your squadron"),
                _(" - !help nearby: commands to find services near you or a specific system, e.g. interstellar factors"),
                _(" - !help search: find the best spots to obtain engineering resources or exobiology"),
                _(" - !help ship: find out where you've parked your ships, evaluate your build, find a fleet carrier parking slot"),
                _(" - !help odyssey: evaluate your storage of materials, know if a material is useful or not"),
                _(" - !help travel: spansh companion, in-game route overview"),
                _(" - !help config: configuration options"),
                _(" - !help hotkeys: hotkeys and macro system"),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "about": {
            "header": _("About EDR"),
            "details": [
                _("ED Recon is a third party plugin for Elite Dangerous. Its purpose is to provide insights about outlaws to traders, explorers, and bounty hunters."),
                _(" - EDR is in beta, is developed by LeKeno, and uses a customized version of Ian Norton's EDMCOverlay for the overlay."),
                _(" - It is TOS compliant because it uses Elite Dangerous's player journal which has been designed for third party consumption."),
                _(" - EDR is free to use but you can support EDR's development and server costs at https://patreon.com/lekeno"),
                _(" - Got feedback or questions? Please file bugs, feature requests or questions at https://github.com/lekeno/edr/issues/"),
                "⚶",
                _("Translations (see https://github.com/lekeno/edr/issues/135)."),
                _(" - Contributions by : Juniper Nomi'Tar [UGC], Tomski [bbFA], Jason Hill, MonkasteR, FrostBit"),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "basics": {
            "header": _("Getting started with EDR"),
            "details": [
                _("EDR will proactively show various insights as you fly around and scan other commanders:"),
                _(" - A summary of recent activity as you jump into a system."),
                _(" - EDR and Inara profile for known outlaws as they are sighted (e.g. scanned) or detected (e.g. chat)."), 
                "⚶",
                _("You can ask EDR for insights by issuing various commands via the in-game chat:"),
                _(" - '!sitrep Lave' to find out if Lave has seen some recent activity."),
                _(" - '!notams' to find out which systems are considered hotspots."),
                _("Learn more with '!help system' and '!help cmdr'"),
                "⚶",
                _("You can also customize EDR to your needs with the cmdrdex features, send '!help cmdrdex' to learn more."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "account": {
            "header": _("EDR account"),
            "details": [
                _("While EDR provides useful information without any credentials, it has a lot more to offer with an account."),
                "⚶",
                _("Important: with an account EDR may report your location to the backend. However, this information will not be shown to other EDR users."),
                _("In the future, this might be used to help enforcers join forces or for check and balance reasons, e.g. reporting outlaw EDR users."),
                "⚶",
                _("An EDR account is free and unlocks all of EDR's features. For instance:"),
                _(" - personalizing / augmenting EDR's commanders database."),
                _(" - reporting of traffic, outlaws, crimes, and fights."),
                _(" - reporting scans of commanders with legal status and bounties."),
                _(" - reporting and getting insights about powerplay enemies."),
                "⚶",
                _("These insights will also help other EDR users so consider applying for an EDR account at https://edrecon.com/account"),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "system": {
            "header": _("Star system related features"),
            "details": [
                _("When jumping to a system, EDR will show a sitrep for the system: active notices, i.e. NOTAM, summary of recent activity, etc."),
                _("Send the following command via the in-game chat to get intel about recent activity or specific systems:"),
                _(" - '!sitreps': to display a list of star systems with sitreps."),
                _(" - '!sitrep': to display the sitrep for the current system."),
                _(" - '!sitrep system_name': to display the sitrep for the star system called system_name."),
                _(" - '!notams': to display a list of star systems with active notices, i.e. Notice To Air Men."),
                _(" - '!notam system_name': to display any active notice the star system called system_name."),
                _(" - '!distance system_name', '!d system_name': to display the distance from your position to 'system_name'."),
                _(" - '!distance A > B', '!d A > B': to display the distance from 'A' to 'B'."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "cmdr": {
            "header": _("Commander related features"),
            "details": [
                _("Use the following chat commands to lookup a commander's profile:"),
                _(" - 'o7': direct message a commander with a salute emoji to see their EDR and Inara profile."),
                _(" - '!who cmdr_name': to see cmdr_name's EDR and Inara profile."),
                _(" - Point at, or salute another player with the emote gestures to show their EDR and Inara profile."),
                _("These commands will show the following information:"),
                _(" - EDR alignment: outlaw, ambiguous, lawful with grades, e.g. outlaw ++++."),
                _(" - User tags: [!12, ?1, +0], i.e. 12 users marked that commander as an outlaw, 1 as neutral, 0 as enforcer."),
                _(" - Inara info: squadron and role if any (sometimes superseded by EDR)."),
                _(" - Personal tags/info from your CmdrDex if any (see !help cmdrdex)."),
                _(" - Legal record: # of clean vs. wanted scans, max and latest known bounties"),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "central": {
            "header": _("EDR Central"),
            "details": [
                _("You can dispatch a request to EDR Central's restricted discord channels."),
                _("The request will automatically include your status (e.g. cmdr name, ship, etc.) and other relevant information."),
                _(" - '!edr your message.' to dispatch a generic message."),
                _(" - '!911 your message.' to dispatch a police request."),
                _(" - '!fuel your message.' to dispatch a fuel request."),
                _(" - '!repair your message.' to dispatch a repair request."),
                _("If the message is successfully sent, you will see a confirmation with a codeword."),
                _("If anyone is available, you should receive a friend request or a direct message."),
                _("Identify trustworthy commanders by asking them for the codeword and checking their profile via EDR."),
                _("Note: abusing this feature will result in revoking your access to EDR features."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "enforcers": {
            "header": _("Enforcers"),
            "details": [
                _("Chat commands for enforcers:"),
                _(" - '!outlaws': to display a list of most recently sighted outlaws and their locations."),
                _(" - '?outlaws [on|off]': to enable/disable realtime alerts for sighted outlaws."),
                _(" - '?outlaws cr 10000': to configure a minimal bounty of 10k cr for the realtime alerts."),
                _(" - '?outlaws ly 150': to configure a maximal distance of 150 ly for the realtime alerts."),
                _(" - '?outlaws [cr|ly] -': to remove the [minimal bounty|maximal distance] for the realtime alerts."),
                _(" - '!where cmdr_name': to display the last sighting of the cmdr called cmdr_name provided that EDR considers them an outlaw."),
                _(" - '#!' or '#?' or '#+': to mark a cmdr as an outlaw, neutral or enforcer (see !help cmdrdex for more details)."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "powerplay": {
            "header": _("Powerplay"),
            "details": [
                _("When pledged to a power, your EDR module will also report powerplay enemies."),
                _("Sitreps will also show any sighted enemies in a dedicated section."),
                _("Chat commands for commanders who have been loyal to their allegiance for more than 30 days:"),
                _(" - '!enemies': to display a list of most recently sighted enemies and their locations."),
                _(" - '?enemies [on|off]': to enable/disable realtime alerts for sighted enemies."),
                _(" - '?enemies cr 10000': to configure a minimal bounty of 10k cr for the realtime alerts."),
                _(" - '?enemies ly 150': to configure a maximal distance of 150 ly for the realtime alerts."),
                _(" - '?enemies [cr|ly] -': to remove the [minimal bounty|maximal distance] for the realtime alerts."),
                _(" - '!where cmdr_name': to display the last sighting of cmdr_name provided that they are an enemy or outlaw."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "cmdrdex": {
            "header": _("Personalizing EDR's commanders database"),
            "details": [
                _("The CmdrDex allows you to customize EDR and helps EDR users make informed guesses about other commanders."),
                _("Your CmdrDex is personal, EDR will only show aggregated stats for the alignment tags."),
                _("General rules for the cmdrdex chat commands:"),
                _(" - '#something' or '#something cmdr_name': to tag a contact or cmdr_name with the 'something' tag, e.g. #pirate jack sparrow."),
                _(" - '-#something' or '-#something cmdr_name': to remove the 'something' tag from a contact or cmdr_name."),
                _(" - '-#' or '-# cmdr_name': to remove a contact or cmdr_name from your cmdrdex."),
                "⚶",
                _("EDR pre-defined tags:"),
                _(" - 'outlaw' or '!': for cmdrs who either attacked you or someone despite being clean and non pledged to an enemy power."),
                _(" - 'enforcer' or '+': for cmdrs who are on the good side of the law and hunt outlaws."),
                _(" - 'neutral' or '?': if you disagree with EDR's classification and want to suppress its warning, or if a commander just seems to go about their own business."),
                _(" - 'friend' or '=': to tag like-minded cmdrs, EDR may infer a social graph from these in the future."),
                "⚶",
                _("Attaching a note:"),
                _(" - '@# <memo>' or '@# cmdr_name memo=something': to attach a note to a contact or cmdr_name, e.g. '@# friendly trader."),
                _(" - '-@#' or '-@# cmdr_name': to remove the custom note from a contact or cmdr_name."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "sqdrdex": {
            "header": _("Tagging allies and enemies of your squadron"),
            "details": [
                _("The Squadron Dex allows you to tag other commanders as allies or enemies of your squadron."),
                _("To use this feature, you will need to be an active member of a squadron on https://inara.cz."),
                _("Read access: Co-pilot and above. Write access: wingman and above. Updating: same or higher rank."),
                _("Updating/Deleting existing entries: same or higher rank than the member who created it."),
                "⚶",
                _("Ally and Enemy tags:"),
                _("Send !help cmdrdex for general usage info."),
                _(" - '#ally' or '#s+': to tag a commander as an ally."),
                _(" - '#enemy' or '#s!': to tag a commander as an enemy."),
                _(" - '-#ally' or '-#s+': to remove an ally tag off a commander."),
                _(" - '-#enemy' or '-#s!': to remove an enemy tag off a commander."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "nearby": {
            "header": _("Finding things around you or a specified system Ⅰ"),
            "details": [
                _(" - '!if' or '!if Lave' to find an Interstellar Factors near your position or Lave."),
                _(" - '!raw' or '!raw Lave' to find a Raw Material Trader near your position or Lave"),
                _(" - '!encoded', !enc' or '!enc Lave' to find an Encoded Data Trader near your position or Lave"),
                _(" - '!manufactured', '!man' or '!man Lave' to find a Manufactured Material Trader near your position or Lave"),
                _(" - '!staging' or '!staging Lave' to find a good staging station near your position or Lave, i.e. large pads, shipyard, outfitting, repair/rearm/refuel."),
                _(" - '!htb', '!humantechbroker' or '!htb Lave' to find a Human Tech Broker near your position or Lave"),
                _(" - '!gtb', '!guardiantechbroker' or '!gtb Lave' to find a Guardian Tech Broker near your position or Lave"),
                _(" - '!nav 12.3 -4.5', '!nav set' or '!nav off' to obtain planetary guidance for getting to a specific location"),
                _(" - '!nav clear', '!nav reset', '!nav next', '!nav previous' to clear or reset custom POIs, or select the next/previous custom POI on a planet"),
                _(" - '!offbeat', '!offbeat Lave' to find a station that hasn't been recently visited near your position or Lave"),
                "⚶",
                _("Send !help nearby2 to see other nearby features. Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "nearby2": {
            "header": _("Finding things around you or a specified system Ⅱ"),
            "details": [
                _(" - '!rrrfc', '!rrrfc Lave < 10' to find a fleet carrier with repair/rearm/refuel near your position or within 10 LY of Lave"),
                _(" - '!rrr', '!rrr Lave < 10' to find a station with repair/rearm/refuel near your position or within 10 LY of Lave"),
                _(" - '!fc J6B', '!fc Recon' to display information about a local fleet carrier with a callsign or name that contains J6B or Recon"),
                _(" - '!station Jameson' to display information about a local station/outpost/... with a name that contains Jameson"),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "search": {
            "header": _("Find the best spots for resources and exobiology"),
            "details": [
                _(" - '!search thing' where thing is either the full name or an abbreviation, e.g. !search cadmium"),
                _(" - '!search thing @system' to specify the system to search around, e.g. !search cadmium @deciat"),
                _(" - Abbreviations consist of the first three letters of a one-word resource, or the first letters of each words separated by a space:"),
                _(" - 'cad' for cadmium, 'a e c d' for abnormal compact emission data."),
                _(" - !search can also be used to look for specific odyssey settlements: !search anarchy, military, -alliance"),
                _(" - Use the command with a few letters to see the supported keywords that contain these letters, e.g. '!search strat"),
                _(" - Some manufactured materials may not always return a result. Use the hints and Elite's galaxy map to find a good spot."),
                _(" - Finally, when jumping into a system, EDR will tell you if it has the right conditions for specific materials, e.g. Imperial Shielding (USS-HGE, +++++)."),
                _(" - The more '+', the higher the chances."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "travel": {
            "header": _("Spansh companion and in-game route overview"),
            "details": [
                _(" - EDR will show an overview for non-trivial in-game routes: scoopable stars, stats and ETA"),
                _(" - EDR also supports Spansh and will place the next waypoint in the clipboard for your convenience, and automatically clear-off surveyed bodies (all species scanned or leaving the body)"),
                _(" - '!journey new <optional destination>' to open Spansh for plotting a new journey, e.g. !journey new colonia"),
                _(" - '!journey fetch' to fetch a Spansh journey from its URL (copy it to the clipboard beforehand)"),
                _(" - '!journey overview', '!journey waypoint', '!journey bodies' to show info about the journey, the current waypoint or bodies to survey"),
                _(" - '!journey next', '!journey previous' to manually change the target waypoint"),
                _(" -  '!journey check <comma separated bodies>' to manually check-off one or more bodies as visited/surveyed, e.g. !journey check 1 a 1, 1 a 2"), 
                _(" - '!journey clear' to clear a currently active journey"),
                _(" - '!journey load <optional filename>' to load a local journey saved in a csv file ('journey.csv' by default), e.g. !journey load myjourney.csv"),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "ship": {
            "header": _("Find where you parked your ship, evaluate your build"),
            "details": [
                _(" - '!ship name_or_type' where name_or_type is either a ship name or type."),
                _(" - '!ship fdl' will show where your Fer-de-Lance ships are parked."),
                _(" - '!ship In Front of Things' will show where your ship(s) named 'In Front of Things' are."),
                _(" - '!eval power' to get an assessment of your power priorities."),
                "⚶",
                _(" - '!parking', '!parking deciat', '!parking deciat #1' to check for fleet carrier parking slots in the current system, Deciat, or the second closest system to Deciat."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "config": {
            "header": _("Configuration options"),
            "details": [
                _("EDR offers the following configuration options:"),
                _(" - !crimes [off|on]: to disable/enable crime and fight reporting, e.g. '!crimes off' before an agreed upon duel."),
                _(" - !audiocue [on|off|loud|soft] to control the audio cues, e.g. '!audiocue soft' for soft cues."),
                _(" - !overlay [on|off|] to enable/disable or verify the overlay, e.g. '!overlay' to check if it is enabled/working."),
                _(" - !gesture [on|off] to control whether gestures can trigger EDR features, e.g. '!gesture off' to disable gesture triggers."),
                _(" - check the instructions in config/igm_config.v9.ini to customize the layout and timeouts."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "odyssey": {
            "header": _("Odyssey"),
            "details": [
                _("EDR offers the following features to help you make sense of Odyssey materials, engineers and exobiology:"),
                _(" - !eval [locker|backpack]: to evaluate the usefulness of materials in your ship locker or backpack, e.g. '!eval locker'. Useful when selling stuff at the bar, or via your fleet carrier."),
                _(" - !eval [name of the material] to evaluate the usefulness of a specific material, e.g. '!eval surveillance equipment'. Useful to assess a reward before accepting a mission."),
                _(" - Point at materials while on foot with the emote gesture to get EDR to identify it and provide info about its usefulness."),
                _(" - !eval [bar|bar demand] to evaluate the items on sale (or in demand) at the last visited bar on a fleet carrier, e.g. '!eval bar demand'. Useful to know which items to buy / sale."),
                _(" - Visit the bar on a fleet carrier to get a list of most useful items on sale, or least useful items in demand."),
                _(" - Exobiology hints and progress tracking when targeting a planet, being in its orbit or by sending the '!biology' command (e.g. '!biology 1 A'"),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        },
        "hotkeys": {
            "header": _("Hotkeys and Macros"),
            "details": [
                _("EDR supports hotkey integration via the EDMCHotkeys plugin."),
                _(" - Bind an Action ID in EDMCHotkeys to trigger an EDR command."),
                _(" - Commands can be any chat command like '!intel', '-if', etc."),
                "⚶",
                _("Macro System:"),
                _(" - '!macro set 1': records the last successful command to macro slot 1."),
                _(" - '!macro set 1 !intel': records '!intel' to macro slot 1."),
                _(" - '!macro show 1': shows the command recorded for macro slot 1."),
                _(" - '!macro name 1 MyName': sets the label for macro slot 1 to 'MyName' (alphanumeric, one word)."),
                _(" - '!macro clear 1': clears macro slot 1."),
                _(" - '!macro list': lists all programmed macro slots."),
                _(" - Programmed macros are saved in config/hotkeys.json."),
                "⚶",
                _("Send !clear in chat to clear everything on the overlay.")
            ]
        }

    }

    def __init__(self, help_file=None):
        if help_file:
            self.content = json.loads(open(os.path.join(plugin_root(), help_file)).read())
        else:
            self.content = HelpContent.DEFAULT_CONTENT

    def get(self, category):
        if category in self.content.keys():
            return self.content[category]
        return None

del _