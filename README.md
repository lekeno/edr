# EDR
ED Recon is an [EDMC](https://github.com/Marginal/EDMarketConnector/) plugin for [Elite: Dangerous](https://www.elitedangerous.com/) whose purpose is to warn you about other dangerous commanders and help bounty hunters chase them. Main developer: LeKeno from Cobra Kai.

# Private beta
EDR is currently in a private beta phase.
If you would like to participate:
 - fill up [this form](https://docs.google.com/forms/d/e/1FAIpQLSeUikUIbKdcjMsWpzB4kX-iPIFvUIaBO2qHD00NveMDvpAnow/viewform)
 - wait for LeKeno to contact you (in-game or over the official forums) with your credentials
 - download the [latest release](https://github.com/lekeno/edr/releases/latest)
 - bookmark [EDR's companion website](https://blistering-inferno-4028.firebaseapp.com/) (early stage)
 - follow the instructions in the **How to** section of this readme.

# How to
## Pre-requisites
 - Platform: Windows (the overlay doesn't work on Mac OS).
 - Have [EDMC installed and configured](https://github.com/Marginal/EDMarketConnector/#installation)
 - Playing [Elite: Dangerous](https://www.elitedangerous.com/) in Open
 - EDR credentials (i.e. user email and password) for full access to all features.

## Install
 1. Donwload and install [EDMC](https://github.com/Marginal/EDMarketConnector/#installation)
 2. Download [LeKeno's EDR plugin](https://github.com/lekeno/edr/releases/latest).
 3. Launch EDMC.
 4. Click on File, then Settings and finally the Plugins tab.
 5. On the Plugins settings tab press the “Open” button. This will reveal the plugins folder where EDMC looks for plugins.
 6. Open EDR's .zip archive and move its content inside an EDR subfolder of the plugins folder.
 7. Re-Launch EDMC, open File > Settings and click on the EDR tab.
 8. Enter your EDR credentials (i.e. email and password) if you got them, or leave blank otherwise.
 9. Click OK, launch Elite, look at the EDR status line. It should say authenticated and then a bunch of things depending on what happens in the game.
 
## Options
Setup the type of feedback that suits you best:
 1. Go to EDR’s options panel from EDMC > File > Settings
 2. Enable visual and/or audio feedback. Note that the visual feedback only works when Elite runs in Windowed or Borderless mode (With Windows 10, the overlay seems to also work in fullscreen).
 3. Click OK.

## Usage
EDR will warn you when dangerous cmdrs make themselves known to the player journal: comms, interdiction, etc.
Alternatively, you can trigger an EDR + Inara cmdr profile lookup by:
 - Sending an ```o7``` to the cmdr you are wondering about.
 - Sending a ```!who <cmdrname>``` on chat (local, wing, etc.)

EDR will also show a sitrep of your destination while jumping, if it had recent activity or a NOTAM. Information shown:
 - NOTAM (e.g. Community Goal, PvP Hub, Known hot spot, etc.)
 - List of recently sighted outlaws and cmdrs
 - List of cmdrs who recently interdicted or killed other cmdrs

### Limited access vs. full access
If you don't have an EDR account, you can still use EDR to get insights about cmdrs and systems. Essentially, any feature that only access existing data should work, e.g. ```!who <cmdrname>```, ```!sitreps```, ```!outlaws```.

With an EDR account, you will be able to report sightings and crimes which will help every EDR users.

### Activity
Send the following command via the in-game chat to get intel about recent activity or specific systems:
 - ```!sitreps``` to display a list of star systems with sitreps
 - ```!sitrep``` to display the sitrep for the current system
 - ```!sitrep <system_name>``` to display the sitrep of a given star system
 - ```!notams``` to display a list of star systems with active NOTAMs
 - ```!notam <system_name>``` to display the NOTAM of a given star system

### Bounty hunting
Send the following command via the in-game chat to get intel about outlaws:
 - ```!outlaws``` to display a list of most recently sighted outlaws and their locations.
 - ```!where <cmdrname>``` to display the last sighting of ```<cmdrname>``` provided that EDR considers them as outlaws.

### CmdrDex
Build your own personalized Commander Index (CmdrDex) to customize your EDR experience and help other EDR users make informed guesses about other commanders' intent. Your CmdrDex is personal, EDR will only show aggregated stats for the alignment tags, e.g. 79% outlaw, 25% neutral, 5% enforcer (abbreviated as ```[!70% ?25%? +5%]``` in-game). 

General chat commands:
 - ```-#``` or ```-# <cmdrname>``` to untag (remove) a contact or <cmdrname> from your commander index.
 - ```#<tag>``` or ```#<tag> <cmdrname>``` to tag a contact or <cmdrname> with a custom <tag> in your commander index.
 - ```-#<tag>``` or ```-#<tag> <cmdrname>``` to remove the <tag> tag from a contact or <cmdrname> in your commander index, e.g. ```#pirate jack sparrow```).

#### Alignment tags
Tag a commander with an alignment tag:
 - outlaw tag if you see them going after a clean and non-enemy power commander.
 - enforcer tag if you have seen them going after an outlaw.
 - neutral tag if you disagree with EDR's classification and want to suppress its warning, or if a commander just seems to go about their own business.
 
Supported chat commands:
 - ```#outlaw``` or ```#!``` to tag a contact with an outlaw tag.
 - ```#outlaw <cmdrname>``` or ```#! <cmdrname>``` to tag <cmdrname> with an outlaw tag.
 - ```#neutral``` or ```#?``` to tag a contact with a neutral tag.
 - ```#neutral <cmdrname>``` or ```#? <cmdrname>``` to tag <cmdrname> with a neutral tag.
 - ```#enforcer``` or ```#+``` to tag a contact with an enforcer tag.
 - ```#enforcer <cmdrname>``` or ```#+ <cmdrname>``` to tag <cmdrname> with an enforcer tag.
 - ```-#<alignnment-tag>``` or ```-#<alignnment-tag> <cmdrname>``` to remove the <alignment-tag> from a contact or <cmdrname> in your commander index.
 
#### Friends
 You can tag a commander with a Friend tag if you are like-minder or fly frequently together. EDR might use this information to infer a social graph.

Supported chat commands:
 - ```#=``` or ```#friend``` to tag a contact with a friend tag.
 - ```#= <cmdrname>``` or ```#friend <cmdrname>``` to tag <cmdrname> with a friend tag.
 - ```-#=``` or ```-#friend <cmdrname>``` to remove a friend tag from a contact or <cmdrname> in your commander index.
 
#### Memo
You can attach a note to a commander so that you remember how you met them or who they are.

Supported chat commands:
 - ```@# <memo>``` to attach a custom note to a contact with <memo> in your commanders index.",
 - ```@# <cmdrname> memo=<memo>``` to attach a custom note to <cmdrname> with <memo> in your commanders index.",
 - ```-@#```` or ```-@# <cmdrname>``` to remove the custom note from a contact or <cmdrname> in your commander index

### Misc.
Control EDR settings by sending the following commands via the in-game chat:
- ```!crimes [on|off]``` to turn on and off EDR's crime reporting feature. For instance, type ```!crimes off``` before engaging in an agreed upon duel
 - ```!audiocue [on/off/loud/soft]``` to control the audio cues
 - ```!overlay [on|off|]``` to enable/disable or verify the overlay


# FAQ
## What does EDR stand for?
Ed’s Didn’t Rebuy plugin ;) ED Recon is the original meaning.

## What is Cobra Kai?
Cobra Kai is a group of cmdrs whose goal is to protect non-combatants and disrupt the players who are on the "wrong side" of the law. Our main focus is on Community Goals, but we perform our duties at other places in the Galaxy as well.

## How does EDR work?
EDR is composed of a plugin and a server.

The EDR plugin relies on the events sent by EDMC whenever an update is made to the Player Journal. This allows EDR to understand where you are and what is happening.

The EDR server provides insights to bounty hunters and law enforcers: where the action is, who committed a crime, where wanted cmdrs are, etc. It also provides the evidence required to adjust a cmdr’s karma and warn other players accordingly.

## Which platforms are supported by EDR?
Windows at the moment. On Mac OS X, the overlay will not work.

## Which game modes are supported by EDR?
EDR only works when you play in Open. It does not send anything when you play in Solo or Private. As a consequence, it will not warn you when you play in Private (and Solo but that would be ridicule in itself ;D).

## What information does EDR collect?
Currently, the following information is collected:

 - traffic information: EDR sends a blip whenever you meet another cmdr, or when a cmdr signals their presence through comms.
 - crimes information: EDR sends a crime report for interdictions and death. It currently does not report stations rams, stray shots and other events without casualties.
 - player status: EDR sends a blip whenever your location changes.

## The overlay layout is a bit off-centered. Can I tweak it?
Yes. You can change the layout by editing the igm_config.ini file in config/ and test with the ```!overlay``` command (after re-launching EDR). Read the instructions in config/config.ini.

## Can I turn off the audio cues?
Yes. You have 2 options.

 - With EDMC, in File > settings, click on EDR and disable the audio feedback option.
 - With the in-game comms, send the following commands:
   - !audiocue off : to disable the audio feedback
   - !audiocue on : to enable the audio feedback

## The audio cues are too loud.
Send !audiocue soft on local/wing/... chat to pick a softer set of sound. To revert: !audiocue loud.

## How does EDR decide to warn about a cmdr?
The server gives EDR a cmdr profile which contains a karma value. The karma value has been set for a small set of cmdr who have been known to behave as outlaws.

## EDR didn’t warn me about cmdr X. Why?
Dynamic karma is still a work in progress. Early take is that there isn't enough information in the player journal. In the meantime, mark them as outlaws (```#! <cmdrname>```) if they attacked you for no legal reason, i.e. you weren't wanted nor pledged to an enemy power. 

## EDR wrongly called out cmdr X as an outlaw / …
Mark them as neutral with ```#= <cmdrname>```.

## EDR’s status displays the status of my friends. Is this information sent as well?
No. The plugin only keeps track of your friends locally. This information is used to determine if a direct message is to one of your friend or a stranger. In the latter case, the plugin can infer that the stranger is in the same location as you are and can report a blip. In the former case, your friend could be anywhere in space so the plugin does not report a blip.

## Does EDR send the content of text comms?
No. EDR has no interest in the content of text comms. It would also be a lot of data to deal with.

## Does this repository contains all the files and depedencies?
No. It doesn't include dependencies like [EDMC Overlay](https://github.com/inorton/EDMCOverlay) nor the configuration info (e.g. API keys, hosts).

# Known bugs
## The overlay stays on top when I switch away from Elite.
This is a known issue with [EDMC Overlay](https://github.com/inorton/EDMCOverlay). The author is aware of it. In the meantime, switch back to Elite and wait until the overlay disappear.

## The audio cue stutters when multiple warnings are sent at once.
The audio cue implementation is a bit simplistic. It shouldn’t occur too often though.

# Acknowledgements
Special thanks to:
 - Fellow Cobra Kai and allies for their help with the initial beta.
 - [Ian Norton](https://github.com/inorton/) for EDMC Overlay and updating it with performance and accuracy improvements.
 - The Elite Dangerous Developers Community.
 
 # Support
 If you like EDR and want to help, consider [becoming a patron](https://www.patreon.com/lekeno/) for as low as 1$ per month. In case you wondered, EDR currently costs me 25$ per month (Firebase's Flame plan).
