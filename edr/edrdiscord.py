import json
from xmlrpc.client import DateTime
import requests
import os
import random
import re
from datetime import datetime, timezone
from binascii import crc32
from hashlib import md5
from numbers import Number
from itertools import dropwhile

import utils2to3
from edri18n import _
from edrconfig import EDRUserConfig, EDRConfig
from lrucache import LRUCache
from edrafkdetector import EDRAfkDetector
from edtime import EDTime
import backoff
from edrlog import EDR_LOG



class EDRDiscordSimpleMessage(object):
    def __init__(self, message):
        self.content = message

    def json(self):
        return self.__dict__


class EDRDiscordMessage(object):
    def __init__(self):
        self.username = "EDR"
        self.avatar_url = "https://lekeno.github.io/icon-192x192.png"
        self.content = ""
        self.embeds = []
        self.tts = False
        self.files = []

    def json(self):
        base = self.__dict__
        base["embeds"] = [ embed.json() for embed in self.embeds]
        return base

    def valid(self):
        if not self.content:
            return False

        for embed in self.embeds:
            if not embed.valid():
                return False

        return True
    
    def add_embed(self, discord_embed):
        self.embeds.append(discord_embed)

    def add_file(self, filename, name):
        with open(filename, "rb") as f:
            self.files.append({"file": f.read(), "filename":name})


class EDRDiscordEmbed(object):
    def __init__(self):
        self.title = ""
        self.url = ""
        self.description = ""
        self.color = 14177041
        self.author = {
            "name": "",
            "url": "",
            "icon_url": ""
        }
        self.fields = []
        self.image = {
            "url": ""
        }
        self.thumbnail = {
            "url": ""
        }
        self.footer = {
            "text": "via ED Recon",
            "icon_url": "https://lekeno.github.io/favicon-16x16.png"
        }
        self.timestamp = datetime.utcnow().isoformat()
    
    def json(self):
        return {
            "title": self.title,
            "url": self.url,
            "description": self.description,
            "color": self.color,
            "author": self.author,
            "fields": [ field.json() for field in self.fields],
            "image": self.image,
            "thumbnails": self.thumbnail,
            "footer": self.footer,
            "timestamp": self.timestamp
        }



class EDRDiscordField(object):
    def __init__(self, name, value, inline=False):
        self.name = name
        self.value = value
        self.inline = inline

    def json(self):
        return {
            "name": self.name,
            "value": self.value,
            "inline": self.inline
        }


class EDRDiscordWebhook(object):
    SESSION = requests.Session()

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.backoff = backoff.Backoff(u"Discord")

    def send_text(self, text):
        if not self.webhook_url:
            return False
        if self.backoff.throttled():
            return False
    
        message = EDRDiscordSimpleMessage(text)
        payload_json = message.json()
        
        return self.__post(payload_json)        

    def send(self, discord_message):
        if not self.webhook_url:
            return False
        if self.backoff.throttled():
            return False
    
        resp = None
        payload_json = discord_message.json()
        if discord_message.files:
            files = discord_message.files
            files["payload_json"] = (None, json.dumps(payload_json))
            return self.__post(payload_json=None, files=files)
        else:
            return self.__post(payload_json)

    def __post(self, payload_json, files=None, attempts=3):
        while attempts:
            try:
                attempts -= 1
                resp = EDRDiscordWebhook.SESSION.post(self.webhook_url, json=payload_json, files=files)
                return self.__check_response(resp)
            except requests.exceptions.RequestException as e:
                EDR_LOG.log(u"ConnectionException {} for POST Discord Webhook: attempts={}".format(e, attempts), u"WARNING")
                last_connection_exception = e
        raise last_connection_exception
    
    def __check_response(self, response):
        if not response:
            return False
        
        if response.status_code in [200, 204, 404, 401, 403, 204]:
            self.backoff.reset()
            pass
        elif response.status_code in [429, 500]:
            self.backoff.throttle()
            pass

        return response.status_code in [200, 204]

# TODO localization
class EDRDiscordIntegration(object):
    def __init__(self, edrcmdrs):
        self.edrcmdrs = edrcmdrs
        self.afk_detector = EDRAfkDetector()
        user_config = EDRUserConfig()
        edr_config = EDRConfig()
        
        players_cfg_path = utils2to3.abspathmaker(__file__, 'config', 'user_discord_players.json')
        try:
            self.channels_players_cfg = json.loads(open(players_cfg_path).read())
        except:
            self.channels_players_cfg = {}

        self.incoming = {
            "afk": EDRDiscordWebhook(user_config.discord_webhook_for_comms("afk")),
            "squadron": EDRDiscordWebhook(user_config.discord_webhook_for_comms("squadron")),
            "squadleaders": EDRDiscordWebhook(user_config.discord_webhook_for_comms("squadronleaders")),
            "starsystem": EDRDiscordWebhook(user_config.discord_webhook_for_comms("starsystem")),
            "local": EDRDiscordWebhook(user_config.discord_webhook_for_comms("local")),
            "wing": EDRDiscordWebhook(user_config.discord_webhook_for_comms("wing")),
            "crew": EDRDiscordWebhook(user_config.discord_webhook_for_comms("crew")),
            "chat": EDRDiscordWebhook(user_config.discord_webhook_for_comms("crew")),
            "voicechat": EDRDiscordWebhook(user_config.discord_webhook_for_comms("voicechat")),
            "player": EDRDiscordWebhook(user_config.discord_webhook_for_comms("player")),
        }
        
        self.outgoing = {
            "broadcast": EDRDiscordWebhook(user_config.discord_webhook_for_comms("broadcast", incoming=False)),
            "squadron": EDRDiscordWebhook(user_config.discord_webhook_for_comms("squadron", incoming=False)),
            "squadleaders": EDRDiscordWebhook(user_config.discord_webhook_for_comms("squadronleaders", incoming=False)),
            "wing": EDRDiscordWebhook(user_config.discord_webhook_for_comms("wing", incoming=False)),
            "crew": EDRDiscordWebhook(user_config.discord_webhook_for_comms("crew", incoming=False)),
            "chat": EDRDiscordWebhook(user_config.discord_webhook_for_comms("crew", incoming=False)),
            "voicechat": EDRDiscordWebhook(user_config.discord_webhook_for_comms("voicechat", incoming=False)),
            "local": EDRDiscordWebhook(user_config.discord_webhook_for_comms("local", incoming=False)),
            "starsystem": EDRDiscordWebhook(user_config.discord_webhook_for_comms("starsystem", incoming=False)),
            "player": EDRDiscordWebhook(user_config.discord_webhook_for_comms("player", incoming=False))
        }

        self.fc = {
            "jump": EDRDiscordWebhook(user_config.discord_webhook_for_fc("jump")),
            "market": EDRDiscordWebhook(user_config.discord_webhook_for_fc("market"))
        }
        
        self.cognitive_novelty_threshold = edr_config.cognitive_novelty_threshold()
        self.cognitive_comms_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.cognitive_outgoing_comms_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())

    def process(self, entry):
        self.afk_detector.process(entry) # TODO move AFK state to player.

        if entry["event"] == "ReceiveText" and entry.get("Channel", "N/A") != "npc":
            return self.__process_incoming(entry)
        elif entry["event"] == "SendText":
            return self.__process_outgoing(entry)
        return False

    def fc_jump_scheduled(self, jump_info):
        if not self.fc or not self.fc["jump"]:
            return False
        dm = self.__create_discord_fc_jump_psa(jump_info)
        if not dm:
            return False

        return self.fc["jump"].send(dm)

    def fc_market_update(self, market_info):
        if not self.fc or not self.fc["market"]:
            return False
        dm = self.__create_discord_fc_market_psa(market_info)
        if not dm:
            return False

        return self.fc["market"].send(dm)

    def __process_incoming(self, entry):
        dm = self.__create_discord_message(entry)
        if not dm:
            return False

        channel = entry.get("Channel", None)
        if channel is None and "From" in entry:
            # multi-crew appears to be incoming but without channel
            if entry["From"] not in ["chat", "voicechat", "wing", "crew", "squadron", "squadronleaders", "starsystem", "local", "friend", "player"]:
                channel = "player"
            else:
                channel = entry["From"]
        if self.afk_detector.is_afk() and self.incoming["afk"] and channel in ["player", "friend"]:
            return self.incoming["afk"].send(dm)
        
        if not (channel in self.incoming and self.incoming[channel]):
            return False

        return self.incoming[channel].send(dm)
    
    def __cmdrname_to_discord_color(self, name):
        saturation = [x / 100 for x in range(10, 91, 20)]
        lightness = [x / 100 for x in range(20, 81, 20)]
        
        hash = crc32(name.encode("utf-8")) & 0xFFFFFFFF
        h = hash % 359
        
        hash //= 360
        s = saturation[hash % len(saturation)]
        
        hash //= len(saturation)
        l = lightness[hash % len(lightness)]

        h /= 360
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        rgb = []
        for c in (h + 1 / 3, h, h - 1 / 3):
            if c < 0:
                c += 1
            elif c > 1:
                c -= 1

            if c < 1 / 6:
                c = p + (q - p) * 6 * c
            elif c < 0.5:
                c = q
            elif c < 2 / 3:
                c = p + (q - p) * 6 * (2 / 3 - c)
            else:
                c = p
            rgb.append(round(c * 255))
        return (rgb[0] << 16) + (rgb[1] << 8) + rgb[2]


    def __create_discord_message(self, entry):
        player = self.edrcmdrs.player
        from_cmdr = entry.get("From", player.name)
        if from_cmdr.startswith("$cmdr_decorate:#name="):
            from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
        
            
        channel = entry.get("Channel", "unknown")
        message = entry.get("Message", "")
             
        
        if self.__unfit(from_cmdr, message, channel):
            return False

        cfg = self.__combined_cfg(from_cmdr, channel)

        sender_profile = self.edrcmdrs.cmdr(from_cmdr, autocreate=False, check_inara_server=False)
        
        description_lut = {
            "player": _(u"Direct"),
            "friend": _(u"Direct"),
            "local": _(u"Local: `{location}`").format(location=player.location.pretty_print()),
            "starsystem": _(u"System: `{location}`").format(location=player.star_system),
            "squadron": _(u"Squadron"),
            "squadleaders": _(u"Squadron Leaders"),
            "wing": _(u"Wing"),
            "crew": _(u"Crew"),
            "chat": _(u"Crew"),
            "voicechat": _(u"Voice"),
            "unknown": _(u"Unknown")
        }
        
        dm = EDRDiscordMessage()
        dm.content = self.__discord_escape(message, add_spoiler_tags=cfg["spoiler"])
        dm.username = cfg["name"]
        dm.avatar_url = cfg["icon_url"]
        dm.tts = cfg["tts"]

        if self.__novel_enough_comms(from_cmdr, entry):
            de = EDRDiscordEmbed()
            de.title = _(u"Channel")
            de.description = description_lut.get(channel, channel)
            de.author = {
                "name": cfg["name"],
                "url": cfg["url"],
                "icon_url": cfg["icon_url"]
            }
            de.timestamp = entry["timestamp"]
            de.color = cfg["color"]
            de.footer = {
                "text": _("via ED Recon on behalf of Cmdr {}").format(player.name),
                "icon_url": "https://lekeno.github.io/favicon-16x16.png"
            }

            if sender_profile:
                df = EDRDiscordField(_(u"EDR Karma"), format(sender_profile.readable_karma(details=True)), True)
                de.fields.append(df)
            
            dm.add_embed(de)
            self.cognitive_comms_cache.set(from_cmdr, entry)
        return dm

    def __create_outgoing_discord_message(self, entry):
        player = self.edrcmdrs.player
        from_cmdr = player.name
        to_cmdr = None
        
        channel = entry.get("To", "unknown")
        message = entry.get("Message", "")
        c_channel = channel
        if c_channel not in ["local", "starsystem", "squadron", "squadleaders", "wing", "crew", "chat", "voicechat"]:
            c_channel = "player"
            to_cmdr = entry.get("To", "unknown")
             
        cfg = self.__combined_cfg(from_cmdr, c_channel)

        sender_profile = self.edrcmdrs.cmdr(from_cmdr, autocreate=False, check_inara_server=False)
        receiver_profile = None
        if to_cmdr:
            receiver_profile = self.edrcmdrs.cmdr(to_cmdr, autocreate=False, check_inara_server=False)
        
        description_lut = {
            "player": _(u"Direct"),
            "friend": _(u"Direct"),
            "local": _(u"Local: `{location}`").format(location=player.location.pretty_print()),
            "starsystem": _(u"System: `{location}`").format(location=player.star_system),
            "squadron": _(u"Squadron"),
            "squadleaders": _(u"Squadron Leaders"),
            "wing": _(u"Wing"),
            "crew": _(u"Crew"),
            "chat": _(u"Crew"),
            "voicechat": _(u"Voice"),
            "unknown": _(u"Unknown")
        }
        
        dm = EDRDiscordMessage()
        dm.content = self.__discord_escape(message, add_spoiler_tags=cfg["spoiler"])
        dm.username = cfg["name"]
        dm.avatar_url = cfg["icon_url"]
        dm.tts = cfg["tts"]

        if self.__novel_enough_comms(from_cmdr, entry):
            de = EDRDiscordEmbed()
            de.title = _(u"Channel")
            de.description = description_lut.get(c_channel, c_channel)
            if to_cmdr:
                de.description += _(" to: {}").format(to_cmdr)
            de.author = {
                "name": cfg["name"],
                "url": cfg["url"],
                "icon_url": cfg["icon_url"]
            }
            de.timestamp = entry["timestamp"]
            de.color = cfg["color"]
            de.footer = {
                "text": _("via ED Recon on behalf of Cmdr {}").format(player.name),
                "icon_url": "https://lekeno.github.io/favicon-16x16.png"
            }

            if sender_profile:
                df = EDRDiscordField(_(u"EDR Karma"), format(sender_profile.readable_karma(details=True)), True)
                de.fields.append(df)
            
            dm.add_embed(de)
            self.cognitive_comms_cache.set(from_cmdr, entry)

        if to_cmdr and self.__novel_enough_outgoing_comms(to_cmdr, entry):
            to_cfg = self.__combined_cfg(to_cmdr, c_channel)
            de = EDRDiscordEmbed()
            de.title = _(u"Receiver")
            de.description = to_cmdr
            de.author = {
                "name": to_cfg["name"],
                "url": to_cfg["url"],
                "icon_url": to_cfg["icon_url"]
            }
            de.timestamp = entry["timestamp"]
            de.color = to_cfg["color"]
            de.footer = {
                "text": _("via ED Recon on behalf of Cmdr {}").format(player.name),
                "icon_url": "https://lekeno.github.io/favicon-16x16.png"
            }

            if receiver_profile:
                df = EDRDiscordField(_(u"EDR Karma"), format(receiver_profile.readable_karma(details=True)), True)
                de.fields.append(df)            
        
            dm.add_embed(de)
            self.cognitive_outgoing_comms_cache.set(to_cmdr, entry)

        return dm


    def __create_discord_fc_jump_psa(self, jump_info):
        player = self.edrcmdrs.player
        from_cmdr = player.name
        channel = "fc"
        
        cfg = self.__combined_cfg(from_cmdr, channel)
        
        sender_profile = self.edrcmdrs.cmdr(from_cmdr, autocreate=False, check_inara_server=False)

        dm = EDRDiscordMessage()
        if not jump_info["to"]:
            dm.content = "`{}` has cancelled their fleet carrier jump ({} | {}).".format(jump_info["owner"], jump_info["name"], jump_info["callsign"])
            return dm
        
        dm.content = "`{}` has scheduled a fleet carrier jump from `{}` to `{}` - `{}`.".format(jump_info["owner"], jump_info["from"], jump_info["to"], jump_info["body"])
        
        dm.username = cfg["name"]
        dm.avatar_url = cfg["icon_url"]
        dm.tts = cfg["tts"]

        de = EDRDiscordEmbed()
        de.title = _(u"Flight Plan")
        departureTime = EDTime()
        departureTime.from_js_epoch(jump_info["at"])
        lockdownTime = EDTime()
        lockdownTime.from_js_epoch(jump_info["lockdown"])
        de.description = _("```From     :    {}\nTo       :    {}\nBody     :    {}\nTime(UTC):    {}```").format(jump_info["from"], jump_info["to"], jump_info["body"], departureTime.as_hhmmss())
        de.author = {
            "name": "{} | {}".format(jump_info["name"], jump_info["callsign"]),
            "url": cfg["url"],
            "icon_url": cfg["icon_url"]
        }
        de.timestamp = datetime.now(timezone.utc).isoformat()
        de.color = self.__colorcoded_fc_access(jump_info["access"])
        de.footer = {
            "text": _("via ED Recon on behalf of Cmdr {}").format(player.name),
            "icon_url": "https://lekeno.github.io/favicon-16x16.png"
        }
        de.thumbnail = {
            "url": "https://lekeno.github.io/fc-jump.png"
        }   

        if sender_profile:
            df = EDRDiscordField(_(u"Landing"), _("```Access   :    {}\nNotorious:    {}\nLockdown(UTC):    {}```").format(self.__readable_fc_docking(jump_info["access"]), self.__readable_fc_notorious(jump_info["allow_notorious"]), lockdownTime.as_hhmmss()), True)
            de.fields.append(df)
        
        dm.add_embed(de)
        return dm

    def __colorcoded_fc_access(self, access):
        colorLUT = {
            "none": 13632027,
            "friends": 4886754,
            "squadron": 16751872,
            "squadronfriends": 16312092,
            "all": 8311585,
        }

        return colorLUT.get(access, 10197915)

    def __readable_fc_docking(self, access):
        dockingLUT = {
            "none": "Owner only",
            "friends": "Friends",
            "squadron": "Squadmates",
            "squadronfriends": "Squadmates & friends",
            "all": "Anybody"
        }
        
        return dockingLUT.get(access, "?")

    def __readable_fc_notorious(self, allow_notorious):
        return _("Allowed") if allow_notorious else _("Not allowed")

    def __create_discord_fc_market_psa(self, market_info):
        player = self.edrcmdrs.player
        from_cmdr = player.name
        channel = "fc"
        
        cfg = self.__combined_cfg(from_cmdr, channel)
        
        sender_profile = self.edrcmdrs.cmdr(from_cmdr, autocreate=False, check_inara_server=False)

        dm = EDRDiscordMessage()
        if not market_info["sales"] and not market_info["purchases"]:
            dm.content = "`{}` no longer trading items at their fleet carrier ({} | {}).".format(market_info["owner"], market_info["name"], market_info["callsign"])
            return dm
        
        trading_kinds =  []
        if market_info["sales"]:
            trading_kinds.append(_("selling"))
        if market_info["purchases"]:
            trading_kinds.append(_("buying"))
        dm.content = "`{}` is {} items at their fleet carrier ({} | {}).".format(market_info["owner"], " & ".join(trading_kinds), market_info["name"], market_info["callsign"])
        
        dm.username = cfg["name"]
        dm.avatar_url = cfg["icon_url"]
        dm.tts = cfg["tts"]

        de = EDRDiscordEmbed()
        de.title = _(u"Bar / Market trading")
        de.description = market_info["summary"]
        de.author = {
            "name": "{} | {}".format(market_info["name"], market_info["callsign"]),
            "url": cfg["url"],
            "icon_url": cfg["icon_url"]
        }
        de.timestamp = datetime.now(timezone.utc).isoformat()
        de.color = self.__colorcoded_fc_access(market_info["access"])
        de.footer = {
            "text": _("via ED Recon on behalf of Cmdr {}").format(player.name),
            "icon_url": "https://lekeno.github.io/favicon-16x16.png"
        }
        de.thumbnail = {
            "url": "https://lekeno.github.io/fc-trade.png"
        }   

        if sender_profile:
            df = EDRDiscordField(_(u"Landing"), _("```Access   :    {}\nNotorious:    {}```").format(self.__readable_fc_docking(market_info["access"]), self.__readable_fc_notorious(market_info["allow_notorious"])), True)
            de.fields.append(df)
            df = EDRDiscordField(_(u"Location"), _("```System:    {}\nBody  :    {}```").format(market_info["location"]["system"], market_info["location"]["body"] or "N/A"), True)
            de.fields.append(df)
        
        dm.add_embed(de)
        return dm

                
    def __process_outgoing(self, entry):
        dm = self.__create_outgoing_discord_message(entry)
        if not dm:
            return False
        command_parts = entry["Message"].split(" ", 1)
        command = command_parts[0].lower()
        if command and command[0] == "!":
            if len(command_parts) < 2:
                return False

            if command == "!discord" and self.outgoing["broadcast"]:
                dm.content = " ".join(command_parts[1:]) # no escaping
                return self.outgoing["broadcast"].send(dm)
            return False

        channel = entry.get("To", None)
        if not channel in self.outgoing:
            channel = "player"

        if not channel in self.outgoing:
            return False
        
        dm.content = self.__discord_escape(entry["Message"])
        return self.outgoing[channel].send(dm)

    def __default_cfg(self, cmdr_name):
        random.seed(len(cmdr_name))
        style = random.choice(["identicon", "retro", "monsterid", "wavatar", "robohash"])
        gravatar_url = u"https://www.gravatar.com/avatar/{}?d={}&f=y".format(md5(cmdr_name.encode('utf-8')).hexdigest(), style)
        default_cfg = {
            "name": cmdr_name,
            "color": 8421246,
            "url": "",
            "icon_url": gravatar_url,
            "image": "",
            "thumbnail": "",
            "tts": False,
            "blocked": False,
            "spoiler": False,
            "mismatching": None,
            "matching": None,
            "min_karma": -1000,
            "max_karma": 1000
        }
        
        profile = self.edrcmdrs.cmdr(cmdr_name, autocreate=False, check_inara_server=True)
        if profile:
            default_cfg["color"] = self.__karma_to_discord_color(profile.readable_karma(prefix=False))
            default_cfg["url"] = profile.url or default_cfg["url"]
            default_cfg["icon_url"] = profile.avatar_url or default_cfg["icon_url"]
            
        return default_cfg

    def __combined_cfg(self, cmdr, channel):
        cfg = self.__default_cfg(cmdr)

        top_level_cfg = self.channels_players_cfg.get("", {})
        channel_level_cfg = self.channels_players_cfg.get(channel, {})

        cfg.update(top_level_cfg.get("", {}))
        cfg.update(top_level_cfg.get(cmdr, {}))

        cfg.update(channel_level_cfg.get("", {}))
        cfg.update(channel_level_cfg.get(cmdr, {}))
        
        return cfg

    def __karma_to_discord_color(self, readable_karma):
        colorLUT = {
            "Outlaw++++": 14368588, "Outlaw+++": 14701123, "Outlaw++": 15099450, "Outlaw+": 15497521, "Outlaw": 15895848,
            "Neutral": 8421246, "Ambiguous": 8421246,
            "Lawful": 12971765, "Lawful+": 11001028, "Lawful++": 9030291, "Lawful+++": 7059554, "Lawful++++": 5088817
        }
        return colorLUT.get(readable_karma, 8421246)

    def __novel_enough_comms(self, sender, new_comms):
        last_comms = self.cognitive_comms_cache.get(sender)
        if last_comms is None:
            return True

        new_edt = EDTime()
        new_edt.from_journal_timestamp(new_comms["timestamp"])
        enough_time_has_passed = new_edt.elapsed_threshold(last_comms["timestamp"], self.cognitive_novelty_threshold)
        
        new_channel = new_comms["Channel"] if "Channel" in new_comms else new_comms.get("To", None)
        last_channel = last_comms["Channel"] if "Channel" in last_comms else last_comms.get("To", None)
        new_from = new_comms["From"] if "From" in new_comms else sender
        last_from = last_comms["From"] if "From" in last_comms else sender

        return enough_time_has_passed or (new_channel != last_channel or new_from != last_from)

    def __novel_enough_outgoing_comms(self, receiver, new_comms):
        last_comms = self.cognitive_outgoing_comms_cache.get(receiver)
        if last_comms is None:
            return True

        new_edt = EDTime()
        new_edt.from_journal_timestamp(new_comms["timestamp"])
        enough_time_has_passed = new_edt.elapsed_threshold(last_comms["timestamp"], self.cognitive_novelty_threshold)
        
        new_channel = new_comms["Channel"] if "Channel" in new_comms else new_comms.get("To", None)
        last_channel = last_comms["Channel"] if "Channel" in last_comms else last_comms.get("To", None)
        new_from = new_comms["From"] if "From" in new_comms else receiver
        last_from = last_comms["From"] if "From" in last_comms else receiver

        return enough_time_has_passed or (new_channel != last_channel or new_from != last_from)

    def __discord_escape(self, message, add_spoiler_tags=False):
        escaped_message = message.replace(u'@', u'@​\u200b')
        if add_spoiler_tags:
            escaped_message = escaped_message.replace(u'||', u'|​\u200b|​\u200b')
            return u"||{}||".format(escaped_message)
        return escaped_message


    def __unfit(self, from_cmdr, message, channel):
        cfg = self.__combined_cfg(from_cmdr, channel)

        if cfg.get("blocked", False):
            EDR_LOG.log(u"blocked in player cfg: {}".format(cfg), u"DEBUG")
            return True

        if cfg["matching"]:
            try:
                if not(any(re.compile(regex).match(message) for regex in cfg["matching"])):
                    EDR_LOG.log(u"no matching in player cfg: {} {}".format(message, cfg["matching"]), u"DEBUG")
                    return True
            except:
                pass
        
        if cfg["mismatching"]:
            try:
                if any(re.compile(regex).match(message) for regex in cfg["mismatching"]):
                    EDR_LOG.log(u"mismatching in player cfg: {} {}".format(message, cfg["mismatching"]), u"DEBUG")
                    return True
            except:
                pass

        if "min_karma" in cfg or "max_karma" in cfg:
            profile = self.edrcmdrs.cmdr(from_cmdr, autocreate=False, check_inara_server=True)
            karma = profile.karma if profile else 0
            karma_check = karma < cfg["min_karma"] or karma > cfg["max_karma"]
            EDR_LOG.log(u"Karma check is {} ({} < karma < {})".format(karma_check, cfg["min_karma"], cfg["max_karma"]), u"DEBUG")
            return karma_check
        
        return False