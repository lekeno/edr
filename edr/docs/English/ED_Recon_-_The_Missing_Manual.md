<div align="center">
  <img Alt="Logo_ED_Recon" src="https://edrecon.com/img/icon-192x192.8422df55.png">
  <h1><a href="https://edrecon.com"><b>ED Recon</b></a>
  <br>
  The Missing Manual</h1>
</div>
<p align=right>Draft by CMDR Lekeno</p>
<p align=right>Translation by CMDR FrostBit</p>

# Summary
- [Install](#_toc162390232)
  - [Pre-requisites](#_toc162390233)
  - [Elite Dangerous Market Connector](#_toc162390234)
  - [ED Recon (aka EDR)](#_toc162390235)
  - [EDR account](#_toc162390236)
- [EDR in a nutshell](#_toc162390237)
  - [Output](#_toc162390238)
  - [Tips & Help](#_toc162390239)
- [Commander Features](#_toc162390240)
  - [Automatic Commander Profiles](#_toc162390241)
  - [Manual Commander Profiles](#_toc162390242)
  - [Annotations on other commanders](#_toc162390243)
    - [Generic commands](#_toc162390244)
    - [Alignment tags](#_toc162390245)
    - [Memo](#_toc162390246)
  - [How to read the profile information](#_toc162390247)
- [EDR Karma](#_toc162390248)
  - [What is the EDR Karma?](#_toc162390249)
  - [How is it calculated?](#_toc162390250)
    - [Extra Details](#_toc162390251)
- [System Features](#_toc162390252)
  - [Sitreps](#_toc162390253)
  - [Distance](#_toc162390254)
  - [Known signals](#_toc162390255)
  - [Information about your destination](#_toc162390256)
  - [Current system](#_toc162390257)
- [Planet Features](#_toc162390258)
  - [Point of Interest](#_toc162390259)
  - [Navigation](#_toc162390260)
  - [Noteworthy Materials](#_toc162390261)
- [Finding Services](#_toc162390262)
- [Materials Features](#_toc162390263)
  - [BGS state dependent materials](#_toc162390264)
  - [Searching for specific materials](#_toc162390265)
  - [Raw materials](#_toc162390266)
    - [Profiles](#_toc162390267)
  - [Odyssey materials](#_toc162390268)
    - [Assessment](#_toc162390269)
    - [Fleet Carrier Bars](#_toc162390270)
- [Ship Features](#_toc162390271)
  - [Where did I park my ship?](#_toc162390272)
  - [Power Priorities](#_toc162390273)
  - [Finding a parking slot for your Fleet Carrier](#_toc162390274)
  - [Landing](#_toc162390275)
- [Squadron Features](#_toc162390276)
  - [Squadron enemies and allies](#_toc162390277)
    - [Tags](#_toc162390278)
- [Bounty Hunting Features](#_toc162390279)
  - [Real-time alerts](#_toc162390280)
  - [Bounty Hunting Stats & Graphs](#_toc162390281)
- [Powerplay features](#_toc162390282)
  - [Powerplay hunting](#_toc162390283)
- [Mining features](#_toc162390284)
- [Exobiology features](#_toc162390285)
  - [Biome insights](#_toc162390286)
    - [System wide info](#_toc162390287)
    - [Planet specific info](#_toc162390288)
  - [Navigation and progress tracking](#_toc162390289)
  - [Searching for an auspicious planet for Exobiology](#_toc162390290)
- [Route HUD](#_toc162390291)
- [Spansh companion](#_toc162390292)
- [Odyssey settlements](#_toc162390293)
- [Discord Integration](#_toc162390294)
  - [Forwarding in-game chat messages](#_toc162390295)
    - [Pre-requisites](#_toc162390296)
    - [Configuring the Discord channels (webhooks)](#_toc162390297)
    - [Features](#_toc162390298)
  - [Sending your Fleet Carrier’s Flight plan to Discord](#_toc162390299)
  - [Sending your Fleet Carrier’s buy/sell orders for commodities and odyssey materials](#_toc162390300)
- [Overlay](#_toc162390301)
  - [Multi-monitors & VR setups](#_toc162390302)
    - [VR placement with SteamVR](#_toc162390303)
  - [Custom overlay](#_toc162390304)
- [Crimes reporting](#_toc162390305)
- [Sounds Effects](#_toc162390306)
  - [Commands and options](#_toc162390307)
  - [Customization](#_toc162390308)
- [Appendix](#_toc162390309)
  - [Troubleshooting](#_toc162390310)
    - [Nothing is displayed / Overlay does not work](#_toc162390311)
  - [Frame rate has dropped significantly](#_toc162390312)
    - [Option 1: turn off Vsync](#_toc162390313)
    - [Option 2: try borderless / windowed / fullscreen](#_toc162390314)
    - [Option 3: try EDR’s alternative UI](#_toc162390315)
  - [Other issues, not resolved?](#_toc162390316)
  - [Privacy Considerations](#_toc162390317)

<br><br><br>

# <a name="_e0h8qpx2dod0"></a><a name="_toc162390232">**Install**</a>
If you get stuck or have any questions, feel free to join [EDR central](https://discord.gg/meZFZPj), the community server for EDR with access to the bot, real-time alerts and troubleshooting support.
## <a name="_n4ae7s2jprh0"></a><a name="_toc162390233"></a>Pre-requisites
- Windows
- Elite: Dangerous
- Elite Dangerous Market Connector (see section A)
- Read and understood EDR's [privacy policy](https://edrecon.com/privacy-policy) and [terms of services](https://edrecon.com/tos). **Proceeding any further implies that you understand and agree to the privacy policy and the terms of services.**
## <a name="_202t4w1sq2jx"></a><a name="_toc162390234"></a>Elite Dangerous Market Connector
**If you already have installed Elite Dangerous Market Connector (EDMC), [skip to the next section](#_v721darz3ctv).**

ED Recon is offered as a plugin for Elite Dangerous Market Connector, a great third-party tool for Elite: Dangerous. Check the [official instructions](https://github.com/EDCD/EDMarketConnector/wiki/Installation-&-Setup) if the explanations below are not enough.

Steps:

1. Read [EDMC’s privacy policy](https://github.com/EDCD/EDMarketConnector/wiki/Privacy-Policy). If you disagree with anything or don’t understand it all, do NOT proceed any further.
2. [Download EDMC’s latest release](https://github.com/EDCD/EDMarketConnector/releases/latest) (the .exe file)
3. Double-click on the downloaded file to install it.
   - Windows may warn you about the file. Click on `more info` then `Run anyway`. If you are concerned, feel free to run an antivirus scan on the downloaded file beforehand.
4. Run Elite Dangerous Market Connector from the Start Menu or Start Screen.
5. Optional: allow EDMC to access Frontier’s API on your behalf (**EDR does NOT use the Frontier API, so feel free to ignore this authentication request**).
## <a name="_v721darz3ctv"></a><a name="_toc162390235"></a>ED Recon (aka EDR)
Steps:

1. [Download EDR’s latest release](https://github.com/lekeno/EDR/releases/latest) (the EDR.v#.#.#.zip file where #.#.# is the version number, e.g. 2.7.5 in the screenshot below)

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/EDR_2.7.5_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/EDR_2.7.5_White.png?raw=true">
      <img alt="Screenshot of the release page of EDR 2.7.5" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/EDR_2.7.5_White.png?raw=true">
    </picture>

2. Launch EDMC.
3. Click on File then Settings.

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_01-02_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_01-02_White.png?raw=true">
      <img alt="How to open EDMC settings" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_01-02_White.png?raw=true">
    </picture>

4. Click on the Plugins tab, then click on Open.

    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_03-04_Black.png?raw=true">
      <source media="(prefers-color-scheme: light)" srcset="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_03-04_White.png?raw=true">
      <img alt="How to go to the plugin tab" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_03-04_White.png?raw=true">
    </picture>

5. Create a sub-folder named `EDR` in the `plugins folder`.

    <img alt="How to access the tab and then the plugins folder" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_05_White.png?raw=true">

6. Extract the content of the Zip file you downloaded at step 2 under this EDR sub-folder.

    <img alt="EDR folder creation" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_06_White.png?raw=true">

7. Relaunch EDMC.
8. You should see an EDR status line (e.g. `EDR: authenticated (guest)`) at the bottom of EDMC:

    <img alt="Location and folder structure of EDR" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_07_White.png?raw=true">

9. Launch Elite, start a new game.
10. You should see an intro message (e.g. `EDR V2.7.5 […]`) overlayed on top of Elite.
    - On Windows 10: the overlay should work for all the modes (Fullscreen, Borderless, Windowed).
    - On Windows 7: the overlay does NOT work in Fullscreen, use Borderless or Windowed instead.
    - If the overlay does not work, see the [troubleshooting](#_2l7rqborubf8) section.
## <a name="_7fegmlsbibv6"></a><a name="_toc162390236"></a>EDR account
EDR works out of the box without any account. However, if you want to contribute information back to EDR and its users, e.g. sending sightings of outlaws, you will need to [apply for an account](https://edrecon.com/account).

Important remarks:

- Applications are manually reviewed to keep a high quality of service. This may take a few weeks.
- If you requested to be contacted over discord: watch for a friend request from LeKeno#8484.
- If you requested to be contacted over email: make sure the email from edrecon.com didn’t end up in your spam folder.

After getting your credentials, open the EDR settings (`File` menu, `Settings`, `EDR` tab) fill up the email and password fields accordingly, and click OK.

<img alt="Where to write email and password in EDMC settings for EDR" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_08_White.png?raw=true">

If everything goes according to plan, you should see “authenticated” in the EDR status line.

<img alt="Location where it is indicated whether the login was successful" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_09_White.png?raw=true">

# <a name="_1fob9te"></a><a name="_toc162390237"></a>**EDR in a nutshell**
EDR offers a wide range of features designed to ease and augment your experience in Elite Dangerous: profile of players based on in-game reports, finding rare materials, assessing the value of odyssey materials, etc. 

These features either trigger automatically depending on what’s happening in the game, or can be triggered by sending EDR commands (e.g. `!who lekeno`) via the in-game chat (any channel), or via the EDR input field in the EDMC window:

<img alt="Alterative position from where to send EDR commands in EDMC" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_10_White.png?raw=true">

### <a name="_ld9uhtijx1hr"></a><a name="_toc162390238"></a>Output
EDR shows various useful information via a graphical overlay and a text UI in the EDMC window. 

- The overlay can also be configured as a standalone window for multi-monitors or VR setups (`File` menu, `Settings`, `EDR` tab, `Overlay` set to `standalone`).
- The text UI can be expanded or collapsed with the checkbox on the right side of the EDR status line in EDMC.
### <a name="_6bupzy6m76jg"></a><a name="_toc162390239"></a>Tips & Help
When starting a new game session, EDR will show a random tip either about the game or EDR itself. 

- Consider sending `!help` to get short and sweet guidance about the various EDR commands.
- You can also request a random tip by sending the `!tip` command, or `!tip edr` for tips about EDR, and `!tip open` for tips about playing in Open.
# <a name="_mwwuek580u2s"></a><a name="_toc162390240"></a>**Commander Features**
## <a name="_3znysh7"></a><a name="_toc162390241"></a>Automatic Commander Profiles
If EDR detects the presence of a potentially dangerous commander (e.g. outlaw), it will automatically show that commander's profile. 
Examples: 

- When receiving a message (direct, local, system, etc.) from an outlaw. 
- Being interdicted by an outlaw.
- Joining / forming a wing with an outlaw. 
- Having an outlaw join a multicrew session.
## <a name="_2et92p0"></a><a name="_toc162390242"></a>Manual Commander Profiles
Targeting another player will reveal their EDR profile. For users with an account, completing a scan will result in submitting the info to the EDR server for the benefit of other EDR users. Alternatively, you can trigger an EDR + Inara cmdr profile lookup by: 

- Sending **`o7`** to the cmdr you are wondering about (direct message).
- Sending **<tt>!who *cmdrname*</tt>** or **<tt>!w *cmdrname*</tt>** via the in-game chat (any channel: local, squadron, wing, system, etc.), or via the EDR input field on the EDMC window. Example: **`!w lekeno`**

EDR will also show key info (hit points, size/class, trends) about your target’s ship/vehicle and the selected submodule if any:

<img alt="Interface integrity and hull and shield of the opponent" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_11.png?raw=true">

## <a name="_tyjcwt"></a><a name="_toc162390243"></a>Annotations on other commanders
You can build your own personalized Commander Index (CmdrDex) to customize your EDR experience and help other EDR users make informed guesses about other commanders' intent. Your CmdrDex is personal, EDR will only show aggregated stats for the alignment tags, e.g. 79% outlaw, 25% neutral, 5% enforcer (abbreviated as [!70% ?25%? +5%] in-game).
### <a name="_3dy6vkm"></a><a name="_toc162390244"></a>Generic commands
- `#=` or `#friend` to tag a contact as a friend.
- <tt>#= *cmdrname*</tt> or <tt>friend *cmdrname*</tt> to tag a specific commander as a friend.
- `-#=` or <tt>-#friend *cmdrname*</tt> to remove a friend tag from a contact or a specific commander in your commander index.
- `#tag` or <tt>#tag *cmdrname*</tt> to tag a contact or *cmdrname* with a custom tag in your commander index (e.g. `#pirate jack sparrow`).
- `-#` or <tt>-# *cmdrname*</tt> to untag (remove) a contact or *cmdrname* from your commander index. (e.g. `-# jack sparrow`).
- `-#tag` or <tt>-#tag *cmdrname*</tt> to remove a specific tag from a contact or cmdrname in your commander index, (e.g. `-#pirate jack sparrow`).
### <a name="_1t3h5sf"></a><a name="_toc162390245"></a>Alignment tags
You can tag a commander with an alignment tag, and help other EDR users make an informed guess about other players.

- Outlaw tag if you see them going after a clean and non-enemy power commander.
- Enforcer tag if you have seen them consistently going after outlaws.
- Neutral tag if you disagree with EDR's classification and want to suppress its warning, or if a commander just seems to go about their own business.

Commands:

- `#outlaw` or `#!` to tag a contact with an outlaw tag. 
- <tt>#outlaw *cmdrname*</tt> or <tt>#! *cmdrname*</tt> to tag a specific commander with an outlaw tag (e.g. `#! Vicious RDCS`).
- `#neutral` or `#?` to tag a contact with a neutral tag.
- <tt>#neutral *cmdrname*</tt> or <tt>#? *cmdrname*</tt> to tag a specific commander with a neutral tag (e.g. `#? filthy neutral jr`).
- `#enforcer` or `#+` to tag a contact with an enforcer tag.
- <tt>#enforcer *cmdrname*</tt> or <tt>#+ *cmdrname*</tt> to tag a specific commander with an enforcer tag (e.g. `#+ lekeno`).
- <tt>-#*alignment-tag*</tt> or <tt>-#*alignment-tag cmdrname*</tt> to remove the *alignment-tag* from a contact or specific commander in your commander index (e.g. `-#+ lekeno`).
### <a name="_vppxm7d89cyd"></a><a name="_toc162390246"></a>Memo
You can attach a memo (short reminder) to a commander. This can be handy to remember how you met them or who they are.

Commands:

- `@# “something very important to remember”` to attach a custom note to a contact.
- `@# *cmdrname* memo=“distant worlds 2”` to attach a custom note to a specific commander.
- `-@#` or <tt>-@# *cmdrname*</tt> to remove the custom note from a contact or a specific commander.
## <a name="_4d34og8"></a><a name="_toc162390247"></a>How to read the profile information
The profile includes some graphs showing historical data for 12 months. The current month is on the right edge, and the axis goes back in time from there (i.e. previous month is the bar on the left side of the last bar on the right).

The upper section contains a combined view (same scale) of clean and wanted scans:

- [Top] Number of clean scans in shades of green: the higher the bar / the greener the bar, the more clean scans have been reported.
- [Bottom] Number of wanted scans:  the lower the bar / the redder the bar, the more wanted scans have been reported.

The lower section shows the commander's largest reported bounty for any given month. The height of the bar is relative to other reported bounties (i.e. tallest bar = overall max bounty, half-height bar = 50% of the overall max bounty). The amount of the bounty is reflected in the color of the bar: the hotter the color, the higher the bounty amount. 

<img alt="Framing interface of a graphical box commander" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_12.png?raw=true">

The text profile includes information from EDR and Inara.

The EDR sections provide various signals to help you make an informed opinion about other commanders. Ultimately, it remains your interpretation and opinion. **As such, always use your best judgment and take full responsibility for your behavior and actions.**

- **EDR Karma:** a value between -1000 and 1000 calculated out of a commander's history of scans & bounties as reported by other EDR users. For convenience the karma value is translated into three labels (Outlaw, Ambiguous +/-, Lawful) with + symbols to indicate the level within a category. Outlaw indicates that this commander has been scanned with a significant bounty, Ambiguous indicates a lack of data or both positive/negative signals, Lawful indicates a streak of clean scans. See [edr-karma](#_2s8eyo1) for more details.
- **Karma tags:** EDR users can tag other commanders with predefined (or custom) tags. This section shows a number (or percentage) of tags for the following predefined categories: outlaw (represented as !), neutral (?), enforcer (represented as +). If you see a commander with misleading user tags, let *Cmdr lekeno* know about it.
- **90 days summary:** summary of scans and bounties as reported by EDR users. Includes the number of clean scans, number of wanted scans, and largest reported bounty.
- **Misc.:** EDR will also show other types of information if relevant (e.g. your custom tags if any) .

The Inara section shows information such as role, squadron, allegiance, etc.

<img alt="Framing interface of a commander" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_13.png?raw=true">

# <a name="_2s8eyo1"></a><a name="_toc162390248"></a>**EDR Karma**
## <a name="_17dp8vu"></a><a name="_toc162390249"></a>What is the EDR Karma?
It's a value between -1000 and 1000 meant to provide a **hint** about how law-abiding or law-breaking a commander has been. This is merely a hint to inform your opinion, in combination with other hints or signals in the game (e.g. seen chasing clean commanders, flying a wanted meta FdL in a mining CG, etc.). **So, always use your best judgment, and take full responsibility for your behavior and actions.**
## <a name="_3rdcrjn"></a><a name="_toc162390250"></a>How is it calculated?
The EDR karma is currently computed on the basis of the value of scans & bounties reported by other EDR users (i.e. one's own legal status or bounties are not taken into account; someone else has to report your legal status or bounty to be taken into account).

At a high level: 

- if a commander is reported as clean, their karma value will increase.
- if a commander is reported as wanted, their karma value will decrease. 
- if a commander is reported with a bounty, their karma value may further decrease. 
- if a commander is scanned but hadn't been seen in a while, before reflecting the new information from the scan, they will see their karma decay: 
  - get the benefit of the doubt with a karma boost toward Ambiguous if they had an Outlaw karma. 
  - get a conservative adjustment with a karma decrease toward Ambiguous if they had a Lawful karma.
### <a name="_26in1rg"></a><a name="_toc162390251"></a>Extra Details
The amount of karma increase / decrease from clean / wanted scan isn't uniform: - The amount is smaller at the edges of the karma scale. In other words, it's harder to get the fourth +, than the third +, and so on. This is meant to put a lot more weight behind each + than it would be possible with a linear scale. 

A bounty report can bring the karma further down, depending on the amount:

- The karma is cut into grades (i.e. the number of +)
- Each grade (including Lawful karma) has an associated bounty threshold. 

If a commander is scanned with a bounty that exceeds this threshold, they will be re-assigned to a more appropriate karma range (i.e. Outlaw+++ instead of Outlaw++). This also applies to commanders with a lawful karma, to prevent trolling incidents, while also avoiding having Lawful++++ commanders abuse their karma to go on a rampage. For commanders who got scanned after being under the radar for a while, EDR will make their Karma decay by an amount that depends on how much time went by since the previous scan (i.e. the longer they went silent, the bigger the decay). There are other subtleties such as time thresholds between scans / bounties reports, or caching aspects on the client side that may affect the computation or reflecting the latest karma value.
# <a name="_lnxbz9"></a><a name="_toc162390252"></a>**System Features**
## <a name="_35nkun2"></a><a name="_toc162390253"></a>Sitreps
EDR will show a situation report (aka sitrep) when starting a new session or after jumping to a new system.

Information can include the following:

- NOTAM: a short memo about the system (e.g. Community Goal, PvP Hub, Known hot spot, etc.)
- A list of recently sighted outlaws and cmdrs
- A list of cmdrs who recently interdicted or killed other cmdrs (without any judgment about the lawfulness of said actions)

Commands:

- `!sitreps` to display a list of star systems with recent activity (good candidates for a `!sitrep` command).
- `!sitrep` to display the sitrep for the current system.
- <tt>!sitrep *system name*</tt> to display the sitrep of a given star system (e.g. `!sitrep deciat`).
- `!notams` to display a list of star systems with active NOTAMs.
- <tt>!notam *system name*</tt> to display the NOTAM of a given star system (e.g. `!notam san tu`).
## <a name="_1ksv4uv"></a><a name="_toc162390254"></a>Distance 
EDR can calculate distances between your position and another system, or between 2 arbitrary systems, as long as they are already known by the community. 

Commands: 

- <tt>!distance *system name*</tt> shows the distance between your location and *system name* (e.g. !distance deciat) 
- <tt>!distance *origin* > *destination*</tt> shows the distance between *origin* and *destination* (e.g. `!distance deciat > borann`)
## <a name="_44sinio"></a><a name="_toc162390255"></a>Known signals
EDR can show an overview of known signals for the current system (e.g. resource extraction sites, combat zones, fleet carrier, stations, etc.)

- The overview is automatically shown when looking at a system map.
- Sending the `!signals` command will manually trigger the overview
## <a name="_2jxsxqh"></a><a name="_toc162390256"></a>Information about your destination
**Odyssey only:** EDR will show key information about your next destination (station, fleet carrier, system). For station or fleet carriers, EDR will show the list of available services, as well as information about the controlling faction (BGS state, government, allegiance and whether the faction is a **P**layer **M**inor **F**action).
## <a name="_6du7k5kxmtsl"></a><a name="_toc162390257"></a>Current system
EDR will show estimated exploration value and key information for stars, planets and systems. This feature triggers on: Discovery Scanner honk, Full Spectrum Scan, and Detailed Surface Scan.
# <a name="_h155t7n0y7jz"></a><a name="_toc162390258"></a>**Planet Features**
## <a name="_z337ya"></a><a name="_toc162390259"></a>Point of Interest
EDR has a list of Points of Interest (e.g. crashed ships, abandoned bases, etc). Guidance will be shown automatically when entering a system with PoI’s, as well as when approaching a body with PoI’s. This includes a navigation feature (heading, distance, altitude, pitch) to help you land near a PoI.
## <a name="_a637l9k80gq9"></a><a name="_toc162390260"></a>Navigation
Manual navigation is also supported (shown when approaching a body or when on the surface of a body).

Commands:

- `!nav 123.21 -32.21` to set the destination based on its Latitude and Longitude.
- `!nav off` to disable the navigation feature
- `!nav set` to set your current Latitude, Longitude as the reference point for the navigation feature.
## <a name="_3j2qqm3"></a><a name="_toc162390261"></a>Noteworthy Materials
When approaching a body, EDR will show a list of noteworthy materials (i.e. materials with a density higher than what's typical across the galaxy). Note: this requires prior actions such as scanning the navigation beacon or analyzing the system with the Full Spectrum Scanner, etc.

See more in [Materials Features](#_4i7ojhp).
# <a name="_1y810tw"></a><a name="_toc162390262"></a>**Finding Services**
EDR can help you find services near you or near a specific system.

Commands

- `!if` or `!if Lave` to find an Interstellar Factors near your position or Lave.
- `!raw` or `!raw Lave` to find a Raw Material Trader near your position or Lave.
- `!encoded`, `!enc` or `!enc Lave` to find an Encoded Data Trader near your position or Lave.
- `!manufactured`, `!man` or `!man Lave` to find a Manufactured Material Trader near your position or Lave.
- `!staging` or `!staging Lave` to find a good staging station near your position or Lave, i.e. large pads, shipyard, outfitting, repair/rearm/refuel.
- `!htb`, `!humantechbroker` or `!htb Lave` to find a Human Tech Broker near your position or Lave.
- `!gtb`, `!guardiantechbroker` or `!gtb Lave` to find a Guardian Tech Broker near your position or Lave.
- `!offbeat`, `!offbeat Lave` to find a station that hasn't been visited recently near your position or Lave (useful to find pre-engineered/pre-upgraded spacesuits & weapons in Odyssey).
- `!rrr`, `!rrr Lave`, ``!rrr Lave < 10`` to find a station with repair, rearm and refuel near your position, or lave, or within a 10 LY radius of Lave.
- `!rrrfc`, `!rrrfc Lave`, `!rrrfc Lave < 10` to find a fleet carrier with repair, rearm and refuel near your position, or lave, or within a 10 LY radius of Lave. Please, double check docking access before heading there!
- `!fc J6B`, `!fc recon`, `!station Jameson` to display information about services at local Fleet Carrier or Stations with a callsign/name containing J6B, Recon, Jameson respectively.
# <a name="_4i7ojhp"></a><a name="_toc162390263"></a>**Materials Features**
## <a name="_2xcytpi"></a><a name="_toc162390264"></a>BGS state dependent materials
When arriving in a new system, EDR will sometimes show a list of materials with estimated likelihoods (mostly from signal sources). If your current inventory is low on a particular material and the likelihood is relatively high, you may want to look for a High Grade Emission source and farm it until you are full (after collecting the mats, exit the game, relaunch, go to supercruise at 0 speed, jump back into the signal, repeat until the timer runs out).
## <a name="_1ci93xb"></a><a name="_toc162390265"></a>Searching for specific materials
Send <tt>!search *resource*</tt> to find a good spot for farming a specific resource (e.g. `!search selenium`). You can use the full name of the resource, or an abbreviation. Most very rare, rare and standard resources (data, raw, manufactured) are supported. Exception: guardian technology related resources. Pro-tip: The name of the system will be copied to the clipboard.

Abbreviations:

- The first 3 letters of a single word resource, e.g. `!search cad` for cadmium, 
- The first letters of each word, separated by spaces for multi-words resources, e.g. `!search c d c` for Core Dynamic Composites.

State dependent resources are best effort, please double check for stale info by looking at the date and state via the galaxy map.

Searching around a specific system can be done by sending a command like such (notice the @systemname bit at the end):

- `!search selenium @deciat`
## <a name="_3whwml4"></a><a name="_toc162390266"></a>Raw materials
When approaching a landable body, EDR will show noteworthy raw materials (high grade) present on a planet if the density exceeds the galactic median (the more +, the better).
### <a name="_gdtgvskllkcx"></a><a name="_toc162390267"></a>Profiles
If you are looking for lower grade raw materials or something specific then you may find that the default raw material notifications are not as useful. You can switch to a different set of materials by sending the !materials command.

For instance, if you are looking for materials to supercharge your FSD, send `!materials fsd`. This will customize the notifications to only show the materials that are used for synthesis FSD injections.

Other commands:

- `!materials` to see the list of profiles available.
- `!materials default` to revert to the default profile (i.e. high grade raw materials)
#### <a name="_7z80x1k2z0uo"></a>*Custom material profiles*
You can also add your own raw material profiles:

1. Make a copy of the `raw_profiles.json` file (see EDR's data folder)
1. Rename it `user_raw_profiles.json`
1. Edit and rename the profiles to your needs.
1. Save the file.
## <a name="_2bn6wsx"></a><a name="_toc162390268"></a>Odyssey materials
### <a name="_6zdzd86kcgy0"></a><a name="_toc162390269"></a>Assessment
EDR will show a quick assessment of odyssey materials on the following events:

- Taking a mission with a mission specific item.
- Pointing at a material with the game’s gesture system (how many blueprints/upgrades/synthesis/techbroker, rarity, typical locations, required by engineers & whether you still need it, …). This also works for Horizons materials.

<img alt="On-foot material analysis interface" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_14.png?raw=true">

- Sending a `!eval backpack`, `!eval locker`, or <tt>!eval *name of the material*</tt> command (e.g. `!eval air quality reports`).
- Setting a purchase or sale order for a material at the fleet carrier bar.

Furthermore, EDR will show an evaluation of the odyssey materials in the player’s backpack or storage on the following events:

- Selling some material to a bar.
- Throwing away some material.

These features are handy because there are **lots** of useless odyssey materials…
### <a name="_lif1gmn9njms"></a><a name="_toc162390270"></a>Fleet Carrier Bars
When visiting a bar with materials on sale, EDR will show you a list of the most useful materials that you might want to consider buying. Each item is followed by a series of letter+number to give further insights into how worthwhile each item is:

- B: number of blueprints using that item
- U: number of upgrades using that item
- X: trading value at station bars
- E: number of engineer unlocks

If a bar has nothing on sale, or nothing useful on sale, then EDR might show a list of the least useful materials that can be sold at the bar. Use this to make room in your inventory by selling the least useful stuff.

You can also trigger these assessments for the last fleet carrier bar that you have visited with the following in-game chat command:

- `!eval bar` or `!eval bar stock` to evaluate items on sale.
- `!eval bar demand` to evaluate items sought by the owner of the fleet carrier.

    <img alt="Example of the interface and materials for the bar" src="https://github.com/GLWine/edr/blob/2.7.5/edr/docs/Assets/IMG_15.png?raw=true">

# <a name="_qsh70q"></a><a name="_toc162390271"></a>**Ship Features**
## <a name="_3as4poj"></a><a name="_toc162390272"></a>Where did I park my ship?
EDR allows you to find where you have parked your ships.

Commands:

- !ship *shiptype* to find ships of a certain type (e.g. !ship mamba)
- !ship *shipname* to find ships with a certain ship name (e.g. !ship Indestructible II)
- !ship *shipid* to find ships with a certain ship ID (e.g. !ship EDR-001)

Note: this feature should also tell you the ETA for a ship to arrive at its destination if you have initiated a transfer.
## <a name="_1pxezwc"></a><a name="_toc162390273"></a>Power Priorities
EDR can assess how good your power priorities are for maximal survival. Note: this feature is a bit flaky due to a bunch of bugs/caveats in Fdev's implementation.

Command:

- !eval power to get an assessment of your power priorities.
- If it doesn't work, look at your right hand side panel, fiddle with the power priorities back and forth and try again.
## <a name="_49x2ik5"></a><a name="_toc162390274"></a>Finding a parking slot for your Fleet Carrier
The !parking command is here to help you find a parking slot for your fleet carrier.

- Send !parking to get information about the parking slots at your current location.
- Try nearby systems by sending !parking #1,  !parking #2, etc, to get information about the parking slots at #1, #2, ... system near your current location.
- Send !parking Deciat or !parking Deciat #3 to look up parking slots in or near Deciat (or a system of your choice).

As always, EDR will copy the system info into your clipboard, so that you can quickly search for it in the galaxy map.

## <a name="_2p2csry"></a><a name="_toc162390275"></a>Landing
EDR will show key info about at a station when docking, as well as the location of the landing pad for coriolis, orbis, fleet carriers, and some specific planetary locations.

# <a name="_h5qlvi1myggd"></a><a name="_toc162390276"></a>**Squadron Features**
## <a name="_147n2zr"></a><a name="_toc162390277"></a>Squadron enemies and allies
If you are part of a squadron on Inara, you can use EDR to tag other players as enemies or allies of your squadron. You will need to be an active member of a squadron on [Inara](https://inara.cz/) and have a sufficiently high rank.

- Read access: Co-pilot and above. 
- Write access: wingman and above.
- Updating/Removing a tag: same or higher rank than the person who tagged the player
### <a name="_1h5xf180ukij"></a><a name="_toc162390278"></a>Tags
Send the following commands to tag another player (e.g. #ally David Braben) or your target (e.g. #ally) as an enemy or ally of your squadron:

- #ally or #s+ to tag a commander as an ally.
- #enemy or #s! to tag a commander as an enemy.
- -#ally or -#s+ to remove an ally tag off a commander.
- -#enemy or -#s! to remove an enemy tag off a commander.
# <a name="_3o7alnk"></a><a name="_toc162390279"></a>**Bounty Hunting Features**
Send the following command via the in-game chat to get intel about outlaws:

- !outlaws to display a list of most recently sighted outlaws and their locations.
- !where *cmdrname* to display the last sighting of *cmdrname* provided that EDR considers them as outlaws.
## <a name="_23ckvvd"></a><a name="_toc162390280"></a>Real-time alerts
Send the following command via the in-game chat to control the real-time alerts about outlaws:

- ?outlaws on to enable the real-time alerts about outlaws.
- ?outlaws off to disable the real-time alerts about outlaws.
- ?outlaws cr 10000 to set a minimum bounty of 10k credits.
- ?outlaws ly 120 to set a maximum distance of 120 light years from your location.
- ?outlaws cr - to remove the minimum bounty condition.
- ?outlaws ly - to remove the maximum distance condition.
## <a name="_27rhbnov5p09"></a><a name="_toc162390281"></a>Bounty Hunting Stats & Graphs
TODO
# <a name="_ihv636"></a><a name="_toc162390282"></a>**Powerplay features**
## <a name="_32hioqz"></a><a name="_toc162390283"></a>Powerplay hunting
If you have been pledged long enough to a power, you can use the following commands to get intel about powerplay enemies:

- !enemies to display a list of most recently sighted enemies and their locations.
- !where cmdrname to display the last sighting of cmdrname provided that EDR considers them as powerplay enemy.
# <a name="_1hmsyys"></a><a name="_toc162390284"></a>**Mining features**
EDR shows various stats and info to help you mine more efficiently (see [this video](https://www.youtube.com/watch?v=1bp_Q3JgW3o) for details):

In addition, EDR will remind you to restock on limpets before leaving the station.
# <a name="_ibheb5s99hbe"></a><a name="_toc162390285"></a>**Exobiology features**
## <a name="_c03djfza2kkw"></a><a name="_toc162390286"></a>Biome insights
### <a name="_3ovq1rcl2cs1"></a><a name="_toc162390287"></a>System wide info
EDR will indicate if a system has planets with the right conditions for Exobiology. The info will show up when jumping into a system, after a discovery honk, or by sending the !biology command without any parameters. Note that the info is a best guess, double check the system map for the presence of biology signals, and consider scanning the system and/or perform a planetary scan for good measure.
### <a name="_7rht61plf9r9"></a><a name="_toc162390288"></a>Planet specific info
EDR can estimate which biological species one might find on a planet depending on its atmospheric conditions and type. The info is shown in the following scenarios:

- When targeting a planet (see the “Expected bio” and “Progress” lines), or by sending the !biology command for a given planet (e.g. !biology A 1): 

- After mapping the whole planet, EDR will update the “Expected bio” info to reflect the actual genuses that you can find on the planet. Note: the species are still EDR’s best guesses.

## <a name="_js51te3wo932"></a><a name="_toc162390289"></a>Navigation and progress tracking
To improve your efficiency with Exobiology activities, EDR provides the following features:

- Key info for the currently tracked species:

From top to bottom:

- Name of the species.
- Credit value of the species.
- Minimum distance required for gene diversity.
- Distance and heading angle from previous samples (if the circle is filled, it means that there is enough distance from a given sample).

- After successfully sampling a species (3 samples), EDR will show your progress so far:

- Number of genus analyzed vs. total number of known genuses.
- Name of the genuses analyzed.
- Number of species analyzed.
- If you encounter other species along the way, you can record their positions for later. This can be done either via the composition scanner (ship, srv), or by using the “pointing” gesture while on foot. 
  - These custom POIs can be cycled through/recalled by sending !nav next or !nav previous commands. 
  - You can also clear the current POI by sending the !nav clear command, and clear all the custom POIs by sending the !nav reset command.
  - Note: these custom POIs are ephemeral (e.g. wiped out when EDMC is closed).

- At the top: heading angle to aim for to be on track.
- Name of the waypoint, time at which the waypoint was recorded.
- Distance.
- Latitude and longitude
- Heading angle at the time the waypoint was recorded.
## <a name="_c0j9tgvek1tg"></a><a name="_toc162390290"></a>Searching for an auspicious planet for Exobiology
Send !search genus to find a nearby planet with known conditions for a given genus (eg !search stratum). You can also use the full species name (eg !search stratum tectonicas), or certain types of planets (eg !search water !search ammonia or !search biology). Tip: send !search with the first letters of a species, genus (or engineering resource).
# <a name="_dcck8a8ifxz0"></a><a name="_toc162390291"></a>**Route HUD**
EDR will show an overview of a route plotted on the galaxy map as long as it’s not trivial (less than 3 jumps) or too complex (more than 50 jumps). This “Route HUD” will also be shown when jumping to the next waypoint of the route.

The HUD provides the following information:

- Names of the current, next, and last systems in the route.
- Non generic names of systems along the way (e.g. system with a bunch of numbers are only shown if they are among the current, next or last system in the route).
- A visual symbol representing whether a system’s primary star is scoopable (circle), or not (cross). Note: the color of the symbol represents the type of the primary star (note that the current waypoint is always in blue).

- Unique or dangerous stars are noted by a descriptive prefix after the name of the system (e.g. Neutron, White Dwarf, Black Hole, etc).
- Stats about the route and your progress.
  - On the starting system, you will find the following information:
    - How many jumps away from the start.
    - Distance from the start.
    - Elapsed time.

- On the next system, you will find the following information:
  - an average of the duration between each jump (e.g. 18 sec/j = 18 seconds per jump).
  - an estimation of your jump speed (e.g. 1780 LY/HR = 1780 light years per hour).



- On the destination system, you will find the following information:
  - How many remaining jumps to reach the destination.
  - Remaining distance to the destination.
  - Estimated remaining time to reach the destination

# <a name="_bh23qed33q2l"></a><a name="_toc162390292"></a>**Spansh companion**
EDR integrates a set of features to make the most of [Spansh](https://spansh.co.uk/), which is a website offering various routing tools, and help you understand how much progress you’ve been making as shown below:

- Start and destination systems.
- Current waypoint and total number of waypoints.
- Number of bodies to check (for certain type of Spansh routes).
- ETA, remaining distance & jumps.
- Stats: LY per hour, Jumps per hour, LY per jumps, time spent between each jump, etc).

Key features:

- Send !journey new to start creating a Spansh route with pre-filled information (e.g. your jump range, your current location). Note that you can also specify a destination (e.g. !journey new colonia).
- Sending !journey fetch will attempt to download a Spansh route from its address/URL. **Note that the address/URL needs to be copied into the clipboard first!**).
- EDR will automatically advance the route as you make your way to the current waypoint and will place the next waypoint in the clipboard for your convenience (i.e. making it easy to plot the route to the next waypoint).
- For more advanced Spansh routes (e.g. road to riches, exomastery), EDR also provides information about which bodies to check at each waypoint. Send !journey bodies to get the detailed list. 
  - EDR will automatically mark a body as done (e.g. mapped for road to riches, fully surveyed or upon leaving for exomastery).
  - You can also manually mark a list of bodies as done by sending the !journey check command (e.g. !journey check 1 A, or !journey check 1 A, 1 B, 2 D)
- Send !journey next or !journey previous to manually adjust the current waypoint.
- If you quit the game midway through a journey, EDR will resume the journey where you left it at the next session.

Other commands:

- !journey overview to display key information about the journey.
- !journey waypoint to display key information about the current waypoint.
- !journey load to manually load a journey from a csv file (journey.csv by default if no parameter is provided).
- !journey clear to tell EDR to no longer follow the journey if any
- Sending !journey without any parameter will attempt to do the right thing each time it’s called:
  - If there is no journey: fetch a Spansh journey from the clipboard if any, or load a local journey if any, or start a new Spansh journey otherwise.
  - If there is a journey, show an overview.
# <a name="_75mdemgkcjb8"></a><a name="_toc162390293"></a>**Odyssey settlements**
You can use the !search command to find specific odyssey settlements. Here are some examples:

- !search anarchy will find the nearest anarchy settlement around your current position.
- !search anarchy @ Lave will find the nearest anarchy settlement around Lave.
- All known types of government are supported (e.g. !search democracy)
- Other supported conditions:
  - BGS states (e.g. !search bust)
  - Allegiances (e.g. !search imperial)
  - Economies (e.g. !search tourism)
- Multiple conditions can be combined to restrict the search (e.g. !search anarchy, military)
- Finally, conditions can also be excluded. For instance, !search anarchy, -military will find the nearest non-military anarchy settlement. Note: by default, EDR excludes war and civil war states but you can revert this by adding these conditions to your command (e.g. !search war, civil war will find the nearest settlement whose state is believed to be either war or civil war).
- Two handy shortcuts are also provided: !search cz to find the nearest settlement that’s likely a combat zone, and !search restore to find the nearest settlement that’s likely abandoned.

**Important**: due to the dynamic nature of Elite Dangerous’ BGS, it’s not 100% guaranteed that the search feature always returns perfect results. Use the info shown by EDR when approaching the settlement to confirm that the actual conditions match what you were expecting.
# <a name="_3hxun3c7voz"></a><a name="_toc162390294"></a>**Discord Integration**
Current discord integration features:

- Forwarding in-game chat messages to a discord channel of your choice.
- Sending Fleet Carrier flight plans to a discord channel of your choice.
- Sending Fleet Carrier Market Orders (buy/sell) for commodities and odyssey materials.
## <a name="_2grqrue"></a><a name="_toc162390295"></a>Forwarding in-game chat messages
You can setup EDR to directly forward in-game chat messages to a discord server and channel of your choice. Please note the following:

- This needs to be configured by you. By default EDR does not forward anything at all.
- If you configure it, then the EDR EDMC plugin will directly send the messages to your discord server/channel. 
- The EDR backend (server) is NOT involved at all. **In other words, your messages are never shared with EDR, nor sent to EDR servers.** 
- *Did I mention that the messages you receive and send remain private? I did? OK, good!*
### <a name="_hykl4r4kebzp"></a><a name="_toc162390296"></a>Pre-requisites
The discord integration requires the following:

- Having [D](http://discord.com)[iscord](http://discord.com), and a personal Discord server (or a server that you can administer or can ask an admin to follow the instructions).
- Read about [webhooks in Discord](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).
### <a name="_lsz3jqogllfv"></a><a name="_toc162390297"></a>Configuring the Discord channels (webhooks)
In the config folder, look for a file named user\_config\_sample.ini and follow the instructions.
### <a name="_sfs4blgzqvlj"></a><a name="_toc162390298"></a>Features
The discord integration offer the following features:
#### <a name="_u64yp7f4ad8y"></a>*Incoming messages*
- Ability to forward messages received over any of the in-game channels (e.g. local, system, wing, squadron, squadron leaders, crew) to a discord server and channel of your choice (configurable per channel). 
- Ability to configure if and how messages are forwarded for each channel and for specific commanders. See customization options below.
- Ability to forward direct messages sent while you are AFK to a discord server and channel of your choice.
#### <a name="_bww4z7pnredf"></a>*Outgoing messages*
- Ability to send specific messages to a discord server and channel of your choice via the !discord in-game chat command (e.g. !discord about to cash in a wing mission, anyone interested in some free credits?)
- Ability to forward messages sent over any of the in-game channels (e.g. local, system, wing, squadron, squadron leaders, crew) to a discord server and channel of your choice (configurable per channel).

<a name="_ppf0jr3anjme"></a>Customization options

You can define a set of baseline conditions for forwarding by EDR. These conditions can be altered for specific channels, and specific commanders.

- blocked: boolean. If set to true, blocks forwarding.
- matching: list of regular expressions. Use this to limit forwarding to messages that match at least one of those regular expressions.
- mismatching: list of regular expressions. Use this to limit forwarding to messages that match none of those regular expressions.
- min\_karma: number between -1000 and 1000. Use this to limit forwarding to messages whose author's EDR karma is more than the value set.
- max\_karma: number between -1000 and 1000. Use this to limit forwarding to messages whose author's EDR karma is less than the value set.
- name: to replace the cmdr name with something of your choice.
- color: to replace the color of the embed showing extra info (RGB in decimal such as 8421246; default: red to green depending on the cmdr's EDR karma).
- url: to replace the link of the embed (default: Inara profile if any).
- icon\_url: to replace the icon in the embed (default: Inara profile picture if any, or an automatically generated unique icon; expects a URL for an image).
- image: use this to force an image in the embed (default: no image; expects a URL for an image).
- thumbnail: use this to force a thumbnail in the embed (default: no thumbnail; expects a URL for an image).
- tts: discord's text-to-speech feature (set to true if you want discord to read this commander's message aloud; need to be on the right discord channel to hear it).
- spoiler: set to true if you want to hide this commander's messages behind a spoiler tag (requires a click to reveal the content).

Example of a [good configuration file](https://imgur.com/a/2fflOo0). Explanation:

- top level is used to set defaults for every commander (e.g. second):
  - messages containing git gud are never forwarded and the sender needs to have an EDR karma higher than -100.
- a commander named Cranky North Star whose messages are always blocked.
- a commander named Chatty Plantain with a renaming rule to force “[NPC] Chatty Plantain” as the cmdr's name, as well as hiding the messages behind a spoiler tag.
- per channel overrides (e.g. player, wing, squadron, squad leaders, crew) which removes the mismatching and karma restrictions.

See the user\_discord\_players.txt file in the config folder for further instructions (your custom file should be named user\_discord\_players.json and should not contain any comments, i.e. no line starting with ;).
## <a name="_vx1227"></a><a name="_toc162390299"></a>Sending your Fleet Carrier’s Flight plan to discord.
You can either send your Flight Plans to EDR's fc-jumps or to a discord channel of your choosing. For the former, select Public in EDR's options (section: Broadcasts). For the latter, you have 2 options:

- (Preferable) Select Direct in EDR's options to have your flight plan go directly to Discord. Check the rest of the instructions in the user\_config\_sample.ini file found in the config folder of EDR.
- Select Private in EDR's options to have your flight plan go to EDR first, and then to discord. This can be useful in case the server owners don't want to directly share the webhook URL to prevent abuse (i.e. abusers can be kicked out of the forwarding logic on the EDR server). Open [this form](https://forms.gle/7pntJRpDgRBcbcfp8) and follow the steps below:
1. [Create a webhook](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks#:~:text=making%20a%20webhook) for the channel in which you want to see the flight plans.
1. Copy the address of this webhook and submit it via [the form](https://forms.gle/7pntJRpDgRBcbcfp8).
1. Wait for a few days / a week. Ping *lekeno* if nothing happens after a week or so.
## <a name="_3fwokq0"></a><a name="_toc162390300"></a>Sending your Fleet Carrier’s buy/sell orders for commodities and odyssey materials
You can send your buy/sale orders for commodities and odyssey materials to a discord channel of your choice. Check the rest of the instructions in the user\_config\_sample.ini file found in the config folder of EDR.

EDR will also place a copy-pastable summary of recent sale/purchase orders at your fleet carrier after you've made changes to your market and/or bar.
# <a name="_1v1yuxt"></a><a name="_toc162390301"></a>**Overlay**
## <a name="_4f1mdlm"></a><a name="_toc162390302"></a>Multi-monitors & VR setups
If you have a multi-monitors setup, or a VR headset, you may want to set the overlay to standalone (File menu, Settings, EDR tab, Overlay dropdown). The overlay will appear as a separate window with a few controls:

- **Top left corner**: drag and drop to move the overlay, double click to maximize / restore.
- **Bottom left corner**: hover to make the overlay transparent.
- **Bottom right corner**: grab to resize the overlay.
- **Top right corner**: hover to make the overlay opaque.
- **Green square in the top middle**: hover to have the overlay be always on top.
- **Red square in the bottom middle**: hover to have the overlay be a regular window (not always on top).
### <a name="_ucucu4xw87pk"></a><a name="_toc162390303"></a>VR placement with SteamVR
1. Launch EDMC
1. Configure EDR settings (EDMC File menu, Settings, EDR tab) with the overlay set to "Standalone"
1. Launch the game in VR
1. Launch a game session
1. The overlay should start automatically, adjust its size and position as needed (outside of VR)
1. Launch SteamVR's dash menu, select "Desktops", and then select the right desktop if multiple exists
1. Click on the +, select EDMCOverlay V1.1.0.0
1. Adjust the position and size in VR
1. Close SteamVR's dash

Also see [these SteamVR patch notes](https://steamcommunity.com/games/250820/announcements/detail/2969548216412141657) for more details.
## <a name="_19c6y18"></a><a name="_toc162390304"></a>Custom overlay
To customize the overlay, make a copy of the igm\_config.v7.ini and igm\_config\_spacelegs.v7.ini, found in the config folder, and rename them to user\_igm\_config.v7.ini and user\_igm\_config\_spacelegs.v7.ini (note if there are higher versions than v7, then use these version numbers instead).

The first file is for configuring the overlay when in a ship or srv, while the second file is for configuring the overlay when on foot.

Follow the instructions in each file to tweak the colors, and positions of various elements / messages. You can also disable specific types of messages. As you make tweaks to the overlay config file, send the !overlay command to reread the layout, display some test data to make further adjustments.
# <a name="_7ykm03m9mvv5"></a><a name="_toc162390305"></a>**Crimes reporting**
If you don’t want to report interactions or fights (e.g. agreed upon PvP), you may want to disable crimes reporting. Note that EDR will continue to report sightings and scans.

- To disable crimes reporting, send !crimes off, or uncheck the “Crimes reporting” option in EDR’s settings panel.
- To enable crimes reporting, send !crimes on, or check the “Crimes reporting” option in EDR’s settings panel.
- You can confirm the current configuration by sending !crimes. 
# <a name="_px07t36ipq8x"></a><a name="_toc162390306"></a>**Sounds Effects**
## <a name="_2ne505w68iuv"></a><a name="_toc162390307"></a>Commands and options
Sound effects can be disabled or enabled from the EDR options in EDMC (File menu, Settings, EDR tab, Feedback section, Sound checkbox)
## <a name="_eq01mflmbzsh"></a><a name="_toc162390308"></a>Customization
To customize the sound effects, make a copy of the sfx\_config.v1.ini file, found in the config folder, and rename it user\_sfx\_config.v1.ini

There are 2 sections, one called [SFX] and another one called [SFX\_SOFT]. The first one is for sounds when EDR's sound effects are set to loud (via !audiocue loud), the second one is for when EDR is set to soft (via !audiocue soft)

- Each line represents a particular kind of EDR event.
- To mute an event, leave the value blank.

Place your custom sounds (wav format only) into the custom sub folder of the sounds folder. 

Then edit the line for the related event to specify your custom sound, including the custom/ prefix.
#### <a name="_2u6wntf"></a>*Type of events*
- startup: when EDR starts at the beginning of a session
- intel: when EDR shows the profile of a neutral/lawful player
- warning: when EDR shows the profile of an outlaw player
- sitrep: when EDR shows a summary of activity for a system (or all systems)
- notify: when EDR shows some info in response to other commands (e.g. !eval, etc)
- help: when EDR shows the help interface via !help
- navigation: when EDR shows/update the navigation UX
- docking: when EDR shows docking guidance
- mining: when EDR shows mining guidance
- bounty-hunting: when EDR shows bounty hunting guidance
- target: when EDR shows information about a target (i.e. shield/hull, sub-module hit points)
- searching: when EDR starts a search for a service or a rare material
- failed: when EDR encounters an error
- jammed: when the EDR servers are too busy to handle your requests
- biology: when EDR shows navigation information for Exobiology activities


# <a name="_99k37ackwpqt"></a><a name="_toc162390309"></a>**Appendix**
## <a name="_2l7rqborubf8"></a><a name="_toc162390310"></a>Troubleshooting
### <a name="_9hpl7g4822xh"></a><a name="_toc162390311"></a>Nothing is displayed / Overlay does not work
#### <a name="_f4n3blkhb3rd"></a>*Check your settings*
Make sure that you haven’t disabled the overlay by mistake.

Steps:

1. Launch EDMC.
1. Click File, then Settings.
1. Click on the EDR tab.
1. Check the overlay box.

1. In Elite, go back to the main menu and start a new game.

Still nothing? Check the next section.
#### <a name="_hjx7y79gl36e">*Allow the overlay to run*</a>
Your antivirus might be preventing the overlay from running by precaution. 

Recommendation: scan the executable, and allow it to run after confirming that it presents no threat.

Steps:

1. Launch EDMC.
1. Click File, then Settings.
1. Click on the Plugins tab, then click on Open.
1. Go inside the EDR sub-folder, and then inside the EDMCOverlay folder.
1. Right click on the edmcoverlay.exe file, select your antivirus scan option.

1. If your antivirus doesn’t complain, double click on the edmcoverlay.exe file and allow it to run if your antivirus prompts you for a confirmation.
## <a name="_mi3ku75gk1th"></a><a name="_toc162390312"></a>Frame rate has dropped significantly
Before trying any of the options below, make sure that your graphics drivers are up-to-date then confirm that the issue still exists.
### <a name="_if27b778i6er"></a><a name="_toc162390313"></a>Option 1: turn off Vsync
1. Go to Elite’s in-game Options:

1. Select the Graphics options:

1. Find Vertical Vsync, under the Display section, and turn it OFF:

1. Retest EDR
### <a name="_38ptisgtkp43"></a><a name="_toc162390314"></a>Option 2: try borderless / windowed / fullscreen
1. Go to Elite’s in-game Options
1. Select the Graphics options
1. Under the Display section, try the different modes, e.g. Borderless / Windowed / Fullscreen, and see if there is one that works better.
### <a name="_wfcag5nkbun2"></a><a name="_toc162390315"></a>Option 3: try EDR’s alternative UI
1. On the right edge of the EDR status, tick the checkbox to reveal EDR’s alternative UI:

1. Info that would have been displayed via the overlay will be displayed in this area
1. Go to EDMC’s settings from the File menu, then the EDR tab
1. Disable the overlay
1. Optional: if you want to superimpose EDMC 
   1. Go to the Appearance tab, select Always on top.
   1. Enable the transparent theme if you want
   1. Go to Elite’s graphics options and select borderless or windowed.
## <a name="_jtlk7zcvsk5j"></a><a name="_toc162390316"></a>Other issues, not resolved?
Feel free to join [EDR central](https://edrecon.com/discord), the community server for EDR with access to the bot, real-time alerts and troubleshooting support. You might also want to share your EDMC log file with LeKeno#8484 over Discord, see below for instructions.

Steps:

1. Simultaneously hit your Windows key and the R key.

1. Type %tmp% (or %temp%) and hit the Enter key.
1. Find the file named EDMarketConnector.log

1. Review and edit its content with notepad (double clicking should open it with notepad) if needed.
1. Share it with LeKeno#8484 over discord.
## <a name="_8ygra6p0k28j"></a><a name="_toc162390317"></a>Privacy Considerations
If you are curious about how EDR works and what it does, you can check the [source code](https://github.com/lekeno/edr/), and since it’s written in Python you can also scrutinize the running code and confirm that it’s identical to the source code published on GitHub. Frontier also [reviewed and praised EDR](https://forums.frontier.co.uk/threads/flying-in-open-last-night-edr-saved-my-life-it-could-save-yours-too.388696/page-15#post-6118053), confirming that its use of the player journal API is within their rules and terms of services.

The first time that you run EDMC while playing the game, you will be redirected to [Frontier's authentication website](https://auth.frontierstore.net/) and prompted for your Elite: Dangerous username and password. This has **nothing to do with EDR**, and **can be outright ignored.** EDR does NOT use Frontier’s authentication API, instead it uses Frontier’s [player journal API](https://forums.frontier.co.uk/threads/commanders-log-manual-and-data-sample.275151/) which only contains information about what is happening in the game and does NOT contain any personal information.

That said, here is why you may still want to authorize EDMC and not worry about it:

- EDMC’s main purpose is, as the name “Market Connector” implies, to share the in-game market information to a [central database](https://github.com/EDSM-NET/EDDN/wiki) for the benefit of everyone. It does so by accessing the market data for the stations you are docked at via Frontier’s authentication API. This is how several tools are able to tell you which systems/stations are buying Low Temperature Diamonds at a high price, find lucrative trading routes, or even which stations have certain modules or ships available.
- Some uninformed (or worse) folks are spreading unsubstantiated claims that this API gives access to your billing information… Now, think about what this would mean: a traded company exposing business sensitive information to third party developers?! It makes absolutely no sense. The API does not expose any such information.
- Refer to [EDMC’s Privacy Policy](https://github.com/Marginal/EDMarketConnector/wiki/Privacy-Policy) to understand how EDMC handles your data.

