#!/usr/bin/env python
# coding=utf-8

import os
import json
import random
import edri18n

def _(message): return message

DEFAULT_TIPS = {
    "EDR tips": [
        _(u"Situation reports (SITREPs) provide a summary of recent activity at a location."),
        _(u"Send !sitreps in chat to get a list of systems with recent activity."),
        _(u"Send !sitrep <system> in chat to get a SITREP for <system>, e.g. !sitrep Lave."),
        _(u"A Notice to Airmen (NOTAM) warns pilots about potential hazards at a location."),
        _(u"Send '!notams' in chat to get a list of systems with Notice to Airmen, i.e. NOTAM."),
        _(u"Send '!notam <system>' in chat to see the NOTAMs associated with a given system, e.g. !notam Lave."),
        _(u"EDR does NOT report crimes committed in Anarchy or Lawless systems."),
        _(u"Scans of SRV are not reported by Elite Dangerous. So, direct message an o7 to run a profile lookup on SRV contacts."),
        _(u"EDR disables itself in Solo, Private Groups and Beta."),
        _(u"Send '!crimes off' in chat to disable EDR's crime reporting, e.g. arranged duel."),
        _(u"Send '!crimes on' in chat to re-enable EDR's crime reporting."),
        _(u"Send '!audiocue soft' in chat if the audio cues are too loud."),
        _(u"Send '!audiocue loud' in chat if the audio cues are too soft."),
        _(u"Send '!audiocue off' in chat to disable the audio cues."),
        _(u"Send '!audiocue on' in chat to enable the audio cues."),
        _(u"Report suspicious contacts by sending them a direct message."),
        _(u"Send an 'o7' to a contact to learn more about them (i.e. inara profile, EDR insights)."),
        _(u"EDR will automatically report interdictions and deaths to help bounty hunters and law enforcers."),
        _(u"Send '!who <cmdrname> in chat to learn more about <cmdrname>, e.g. !who lekeno"),
        _(u"Send '!overlay off' in chat to disable the in-game overlay."),
        _(u"Send '!overlay on' in chat to enable the in-game overlay."),
        _(u"Send '!overlay' in chat to check the status of the in-game overlay."),
        _(u"Follow the instructions in igm_config.ini to customize EDR's layout."),
        _(u"EDR will automatically report other commanders if they say something on local chat."),
        _(u"EDR will automatically report other commanders if they direct message you (unless they are on your friends list)."),
        _(u"EDR will warn you about outlaws if they reveal themselves or if you report them"),
        _(u"Your EDR account is tied to your cmdr name, do NOT share your credentials with someone else or a different cmdr account."),
        _(u"Sending '-#' to a contact will remove them from your commanders index."),
        _(u"Send '-# <cmdrname>' to remove <cmdrname> from your commanders index."),
        _(u"Sending '#!' or '#outlaw' to a contact will tag them as an outlaw in your commanders index."),
        _(u"Send '#! <cmdrname>' or '#outlaw <cmdrname>' to tag <cmdrname> as an outlaw in your commanders index."),
        _(u"Sending '#?' or '#neutral' to a contact will tag them as neutral in your commanders index."),
        _(u"Send '#? <cmdrname>' or '#neutral <cmdrname>' to tag <cmdrname> as neutral in your commanders index."),
        _(u"Sending '#+' or '#enforcer' to a contact will tag them as an enforcer in your commanders index."),
        _(u"Send '#+ <cmdrname>' or '#enforcer <cmdrname>' to tag <cmdrname> as an enforcer in your commanders index."),
        _(u"Sending '#=' or '#friend' to a contact will tag them as a friend in your commanders index."),
        _(u"Send '#= <cmdrname>' or '#friend <cmdrname>' to tag <cmdrname> as a friend in your commanders index."),
        _(u"Sending '#<tag>' to a contact will tag them as <tag> in your commanders index."),
        _(u"Send '#<tag> <cmdrname>' to tag <cmdrname> as <tag> in your commanders index."),
        _(u"EDR will use the friend tag to infer a social graph for upcoming features."),
        _(u"Your commanders index is personal. EDR will only show aggregate stats to other EDR users."),
        _(u"Tag a commander with an outlaw tag if you witness them going after a clean and non-enemy power commander."),
        _(u"Tag a pirate with an outlaw tag if you witness them destroying a co-operating ship."),
        _(u"Tag a commander with an enforcer tag if you have seen them going after an outlaw."),
        _(u"Tag a commander with a neutral tag if you disagree with EDR's classification."),
        _(u"Tag a commander with a friend tag if you are like-minded and/or fly often together."),
        _(u"Tag a commander with a custom tag for your own needs, e.g. #pirate."),
        _(u"Sending '@# <memo>' to a contact will attach a custom note with <memo> in your commanders index."),
        _(u"Sending '@# <cmdrname> memo=<memo>' will attach a custom note with <memo> on <cmdrname> in your commanders index."),
        _(u"Send '-@' to a contact to remove any attached note in your commanders index."),
        _(u"Send '-@ <cmdrname>' to remove the note attached to <cmdrname> in your commanders index."),
        _(u"In an Intel response, [!70% ?20% +10%] shows the percentage of outlaw (!), neutral (?) and enforcer (+) tags set by other EDR users."),
        _(u"In an Intel response, [!3 ?0 +0] shows the number of outlaw (!), neutral (?) and enforcer (+) tags set by other EDR users."),
        _(u"Have a suggestion for a tip? File an issue at https://github.com/lekeno/edr/issues"),
        _(u"Found a bug? File an issue at https://github.com/lekeno/edr/issues"),
        _(u"Have a feature request? File an issue at https://github.com/lekeno/edr/issues"),
        _(u"Do you like EDR? Consider supporting its development and hosting costs at https://patreon.com/lekeno"),
        _(u"Send '!where <cmdrname>' to find out where an outlaw was last sighted"),
        _(u"Send '!outlaws' to find out where outlaws were last sighted"),
        _(u"Send '!clear' to clear everything on EDR's overlay")
    ],
    "OPEN tips": [
        _(u"Never fly what you can't afford to lose. Check your rebuy and credit balance on your right panel."),
        _(u"Never combat log in Open. If you aren't willing to accept the risk, don't bother with Open, Google 'Mobius PVE'."),
        _(u"Hit Ctrl+B to display a bandwidth meter. You are not alone if it goes over 1000 B/s."),
        _(u"Regularly check your contact history in the top panel for known threats."),
        _(u"[Planet] Dismiss your ship immediately after boarding your SRV. Outlaws will destroy it in seconds otherwise."),
        _(u"[Planet] Switch your SRV lights off if an outlaw shows up. Run far away before calling back your ship."),
        _(u"[Planet] For new discoveries, land a bit away from the area of interest and dismiss your ship asap."),
        _(u"[Explorers] Don't trust anyone, check a contact's loadout in your left panel before banding to take selfies."),
        _(u"[Explorers] On your trip back to the bubble, reach out to Iridium Wing for an escort."),
        _(u"[Explorers] Throttle down to 0% when your jump completes to avoid bad surprises (e.g. neutron star, 2 stars close to each other)"),
        _(u"[Traders] Don't be greedy, use your biggest slot for a shield not for cargo!"),
        _(u"[Traders] Pledge for 4 weeks to Aisling Duval in order to get the stronger 'prismatic shields'."),
        _(u"[Traders] Engineer regular shields with Thermal Resistance, shield boosters with Heavy Duty."),
        _(u"[Traders] Engineer prismatic shields with Reinforced, even resistance % with Augmented Resistance on your shield boosters."),
        _(u"[Traders] Rares are special goods (e.g. Hutton Mug, Sothis Gold). The further you take them from where you buy them (up to 200ly) the more you get for them."),
        _(u"[Suicide trap] At busy stations, stay below 100 m/s or you will get killed by the station for colliding into a 'suicide eagle'."),
        _(u"[Suicide trap] Advanced trap: force shells may push you over the 100m/s safe speed limit. Watch out for wings/duo and cannons loadouts."),
        _(u"[Anti-suicide trap] Buy an eagle, remove its shield, ram the suicide eagle before they destroy another ship."),
        _(u"[Anti-suicide trap] Stay under 100 m/s and ram the suicide eagle before they destroy another ship."),
        _(u"[Anti-suicide trap] Warn other commanders about the presence of a 'suicide eagle' as they approach or leave the station."),
        _(u"[Powerplay hunters] Watch out for powerplay hunters at stations in enemy territory: fighting back will get you wanted."),
        _(u"[Anarchy] Watch for suspicious pilots, they can safely hunt/ram you even if you are clean (station and security won't retaliate)."),
        _(u"[Station] The station fires back when hit. Use that to your advantage: stay close to the structure, chaff, etc."),
        _(u"[Station] The no-fire zone is a misnomer: players can and will fire at you at the cost of a small fine."),
        _(u"[Escape] Bind a key/button to 'select next route' to quickly target your escape route."),
        _(u"[Escape] It is safer and faster to jump to a different system than going back to supercruise (i.e. 'high waking' is not subject to mass lock)."),
        _(u"[Interdiction] Do NOT attempt to win a player interdiction, instead submit to get a faster FSD cooldown."),
        _(u"[Interdiction] Type-7's have a high yaw rate which comes handy when fighting interdictions."),
        _(u"[Community Goal] Consider setting camp at a nearby system with a decent station instead of going straight for the CG system/station"),
        _(u"[Community Goal] Drop just before being interdicted, throttle to zero, charge your FSD, boost when the player shows up. Repeat."),
        _(u"[Supercruise] Don't supercruise straight to the station, take a curve above the plane: faster and safer."),
        _(u"[Supercruise] Go around planets and other stellar objects as they will slow you down."),
        _(u"[Supercruise] 'Ride the 6': keep max speed until the countdown reaches 6 seconds, then middle of the blue zone."),
        _(u"[Supercruise] If your destination is near a planet, have the planet behind you and use its gravity well to slow you down."),
        _(u"[Combat] Put all 4 pips to SYS when being fired upon; move them where needed when not fired upon."),
        _(u"[Combat] Don't fly in a straight line, you'll die if you do. Be evasive: combine rolls, turns, thrusters, boost and Fligh Assist Off."),
        _(u"[Combat] When shields drop, target specific modules. In particular: power plant, drives, biweave shields, weapons."),
        _(u"[Combat] Double shield cell banking: fire first cell, wait for 90% heat, fire heat sink, when heat drops rapidly fire the second cell."),
        _(u"[Combat] Railgun with feedback cascade can counter shield cell banking."),
        _(u"[Combat] Best time to fire your shield cell is when you are at 1 / 1.5 ring and right in front of your opponent just as you are about to fly past them."),
        _(u"[Interdicted] Put 4 pips to SYS, 2 to ENG and fly evasive. Hit next route and high wake asap, do not fly in a straight line."),
        _(u"[Pirates] Follow their instructions and you will avoid a certain death."),
        _(u"[Fuel] Mnemonics for fuel scoopable stars: KGB FOAM or 'Oh Be A Fine Girl Kiss Me'."),
        _(u"[Fuel] Out of fuel? Call the fuel rats (https://fuelrats.com/)."),
        _(u"[Bounty hunting] Don't steal kills. Instead, ask to join a wing: everyone will get the same bounty and way faster."),
        _(u"[Community] Most players are just nice folks. Chat with people, make friends. It might come handy."),
        _(u"[Defense] Fit Point Defenses to your ship to destroy missiles and mines"),
        _(u"[Defense] Like the song says you've got to know when to walk away and know when to run.")
    ]
}

del _

class RandomTips(object):

    def __init__(self, tips_file=None):
        global DEFAULT_TIPS
        if tips_file:
            self.tips = json.loads(open(os.path.join(
                os.path.abspath(os.path.dirname(__file__)), tips_file)).read())
        else:
            self.tips = DEFAULT_TIPS

    def tip(self):
        category = random.choice(self.tips.keys())
        return edri18n._(random.choice(self.tips[category]))