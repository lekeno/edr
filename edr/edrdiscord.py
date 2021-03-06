import json
import requests
import os
from datetime import datetime
from binascii import crc32
from numbers import Number
from itertools import dropwhile

import utils2to3
from edri18n import _
from edrconfig import EDRUserConfig, EDRConfig
from lrucache import LRUCache
from edrafkdetector import EDRAfkDetector
import backoff

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
        # TODO files
        print(base)
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
        print(self.fields)
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
    
        message = DiscordSimpleMessage(text)
        payload_json = message.json()
        resp = EDRDiscordWebhook.SESSION.post(self.webhook_url, json=payload_json)
        return self.__check_response(resp)

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
            resp = EDRDiscordWebhook.SESSION.post(self.webhook_url, files=files)
        else:
            resp = EDRDiscordWebhook.SESSION.post(self.webhook_url, json=payload_json)
        return self.__check_response(resp)

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
            self.players_cfg = json.loads(open(players_cfg_path).read())
        except:
            self.players_cfg = {}

        self.incoming = {
            "afk": {"wh": EDRDiscordWebhook(user_config.discord_webhook("afk")), "tts": user_config.discord_tts("afk")},
            "squadron": {"wh": EDRDiscordWebhook(user_config.discord_webhook("squadron")), "tts": user_config.discord_tts("squadron")},
            "squadleaders": {"wh": EDRDiscordWebhook(user_config.discord_webhook("squadronleaders")), "tts": user_config.discord_tts("squadronleaders")},
            "starsystem": {"wh": EDRDiscordWebhook(user_config.discord_webhook("starsystem")), "tts": user_config.discord_tts("starsystem")},
            "local": {"wh": EDRDiscordWebhook(user_config.discord_webhook("local")), "tts": user_config.discord_tts("local")},
            "wing": {"wh": EDRDiscordWebhook(user_config.discord_webhook("wing")), "tts": user_config.discord_tts("wing")},
            "crew": {"wh": EDRDiscordWebhook(user_config.discord_webhook("crew")), "tts": user_config.discord_tts("crew")},
            "player": {"wh": EDRDiscordWebhook(user_config.discord_webhook("player")), "tts": user_config.discord_tts("player")},
        }
        
        self.outgoing = {
            "broadcast": EDRDiscordWebhook(user_config.discord_webhook("broadcast", incoming=False)),
            "squadron": EDRDiscordWebhook(user_config.discord_webhook("squadron", incoming=False)),
            "squadleaders": EDRDiscordWebhook(user_config.discord_webhook("squadronleaders", incoming=False)),
            "wing": EDRDiscordWebhook(user_config.discord_webhook("wing", incoming=False)),
            "crew": EDRDiscordWebhook(user_config.discord_webhook("crew", incoming=False))
        }

        self.cognitive_novelty_threshold = edr_config.cognitive_novelty_threshold()
        self.cognitive_comms_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())

    def process(self, entry):
        self.afk_detector.process(entry) # TODO move AFK state to player.

        if entry["event"] == "ReceiveText" and entry["Channel"] != "npc":
            return self.__process_incoming(entry)
        elif entry["event"] == "SendText":
            return self.__process_outgoing(entry)
        return False

    def __process_incoming(self, entry):
        dm = self.__create_discord_message(entry)

        channel = entry.get("Channel", None)
        if self.afk_detector.is_afk() and self.incoming["afk"] and channel in ["player", "friend"]: # TODO verify the friend thing : doesn't exist??
            dm.tts |= self.incoming["afk"]["tts"]
            return self.incoming["afk"]["wh"].send(dm)
        
        if not (channel in self.incoming and self.incoming[channel]):
            # TODO: support voicechat channel?
            return False

        dm.tts |= self.incoming[channel]["tts"]
        return self.incoming[channel]["wh"].send(dm)
    
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
             
        cfg = self.__default_cfg(from_cmdr)
        if from_cmdr in self.players_cfg:
            if self.players_cfg[from_cmdr].get("blocked", False):
                return False
            cfg.update(self.players_cfg[from_cmdr])

        sender_profile = self.edrcmdrs.cmdr(from_cmdr, autocreate=False, check_inara_server=False)
        
        channel = entry.get("Channel", "unknown")
        description_lut = {
            "player": _(u"Direct"),
            "friend": _(u"Direct"),
            "local": _(u"Local: `{location}`").format(location=player.location.pretty_print()),
            "starsystem": _(u"System: `{location}`").format(location=player.star_system),
            "squadron": _(u"Squadron"),
            "squadleaders": _(u"Squadron Leaders"),
            "wing": _(u"Wing"),
            "crew": _(u"Crew"),
            "unknown": _(u"Unknown")
        }
        
        dm = EDRDiscordMessage()
        dm.content = entry["Message"] # TODO can this be abused with @here @everyone?
        dm.username = cfg["name"]
        dm.avatar_url = cfg["icon_url"]
        dm.tts = cfg["tts"]

        if self.__novel_enough_comms(from_cmdr, entry):
            de = EDRDiscordEmbed()
            de.title = _(u"Channel")
            de.description = description_lut[channel]
            de.author = {
                "name": cfg["name"],
                "url": cfg["url"],
                "icon_url": cfg["icon_url"]
            }
            de.timestamp = entry["timestamp"]
            de.color = cfg["color"]
            de.footer = {
                "text": "via ED Recon on behalf of Cmdr {}".format(player.name),
                "icon_url": "https://lekeno.github.io/favicon-16x16.png"
            }

            if sender_profile:
                df = EDRDiscordField(_(u"EDR Karma"), format(sender_profile.readable_karma(details=True)), True)
                de.fields.append(df)
            
            dm.add_embed(de)
            self.cognitive_comms_cache.set(from_cmdr, entry)
        return dm

                
    def __process_outgoing(self, entry):
        dm = self.__create_discord_message(entry)
        command_parts = entry["Message"].split(" ", 1)
        command = command_parts[0].lower()
        if command and command[0] == "!":
            if len(command_parts) < 2:
                return False

            if command == "!discord" and self.outgoing["broadcast"]:
                dm.content = " ".join(command_parts[1:]) # no escaping because it seems fine to be able to send @here?
                return self.outgoing["broadcast"].send(dm)
            return False

        channel = entry.get("Channel", None)
        if not channel in self.outgoing:
            return False
        
        return self.outgoing[channel].send(dm)

    def __default_cfg(self, cmdr_name):
        # TODO replace cmdr to discord color with a ambiguous color code
        default_cfg = {
            "name": cmdr_name,
            "color": 8421246,
            "url": "",
            "icon_url": "",
            "image": "",
            "thumbnail": "",
            "tts": False,
            "blocked": False
        }
        profile = self.edrcmdrs.cmdr(cmdr_name, autocreate=False, check_inara_server=True)
        if profile:
            default_cfg["color"] = self.__karma_to_discord_color(profile.readable_karma(prefix=False))
            default_cfg["url"] = profile.url
            default_cfg["icon_url"] = profile.avatar_url

        return default_cfg

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

        delta = new_comms["timestamp"] - last_comms["timestamp"]
        
        return (new_comms["Channel"] != last_comms["Channel"] or new_comms["From"] != last_comms["From"]) or delta > self.cognitive_novelty_threshold