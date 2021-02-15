import json
import requests
import os
from datetime import datetime
from binascii import crc32
from numbers import Number
from itertools import dropwhile

import utils2to3
from edri18n import _
from edrconfig import EDRUserConfig 
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
        base["embeds"] = [ embed.__dict__ for embed in self.embeds]
        # TODO files
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
            "text": "Message sent via ED Recon",
            "icon_url": "https://lekeno.github.io/favicon-16x16.png"
        }
        self.timestamp = datetime.utcnow().isoformat()


class EDRDiscordField(object):
    def __init__(self):
        self.name = ""
        self.value = ""
        self.inline = False

    def json(self):
        return self.__dict__


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

class EDRDiscordIntegration(object):
    def __init__(self, player):
        self.player = player
        self.afk_detector = EDRAfkDetector()
        user_config = EDRUserConfig()
        
        self.blocked_users = []
        blocked_users_cfg_path = utils2to3.abspathmaker(__file__, 'config', 'user_blocklist.txt')
        if os.path.exists(blocked_users_cfg_path):
            with open(blocked_users_cfg_path,'r') as fh:
                for curline in dropwhile(lambda s: s.startswith('; '), fh):
                    self.blocked_users.append(curline.rstrip('\n'))

        self.incoming = {
            "afk": EDRDiscordWebhook(user_config.discord_webhook("afk")),
            "squadron": EDRDiscordWebhook(user_config.discord_webhook("squadron")),
            "squadronleaders": EDRDiscordWebhook(user_config.discord_webhook("squadronleaders")),
            "starsystem": EDRDiscordWebhook(user_config.discord_webhook("starsystem")),
            "local": EDRDiscordWebhook(user_config.discord_webhook("local")),
            "wing": EDRDiscordWebhook(user_config.discord_webhook("wing")),
            "crew": EDRDiscordWebhook(user_config.discord_webhook("crew")),
            "player": EDRDiscordWebhook(user_config.discord_webhook("player"))
        }
        
        self.outgoing = {
            "broadcast": EDRDiscordWebhook(user_config.discord_webhook("broadcast", incoming=False)),
            "squadron": EDRDiscordWebhook(user_config.discord_webhook("squadron", incoming=False)),
            "squadronleaders": EDRDiscordWebhook(user_config.discord_webhook("squadronleaders", incoming=False)),
            "wing": EDRDiscordWebhook(user_config.discord_webhook("wing", incoming=False)),
            "crew": EDRDiscordWebhook(user_config.discord_webhook("crew", incoming=False))
        }

    def process(self, entry):
        self.afk_detector.process(entry) # TODO move AFK state to player.

        if entry["event"] == "ReceiveText" and entry["Channel"] != "npc":
            return self.__process_incoming(entry)
        elif entry["event"] == "SendText":
            return self.__process_outgoing(entry)
        return False

    def __process_incoming(self, entry):
        from_cmdr = entry["From"]
        if entry["From"].startswith("$cmdr_decorate:#name="):
            from_cmdr = entry["From"][len("$cmdr_decorate:#name="):-1]
             
        if from_cmdr in self.blocked_users:
            return False
        
        channel = entry.get("Channel", None)
        dm = EDRDiscordMessage()
        dm.content = ""
        de = EDRDiscordEmbed()
        de.title = ""
        de.description = entry["Message"]
        de.author = {
            "name": from_cmdr,
            "url": "",
            "icon_url": ""
        }
        de.timestamp = entry["timestamp"]
        de.color = self.__cmdrname_to_discord_color(from_cmdr)
        de.footer = {
            "text": "Message sent via ED Recon on behalf of Cmdr {}".format(self.player.name),
            "icon_url": "https://lekeno.github.io/favicon-16x16.png"
        }
        
        if self.afk_detector.is_afk() and self.incoming["afk"] and channel in ["player", "friend"]: # TODO verify the friend thing
            dm.content = _(u"Direct message received while AFK @ `{}`".format(self.player.location.pretty_print()))
            de.title = _("To Cmdr `{}`").format(self.player.name)
            dm.add_embed(de)
            return self.incoming["afk"].send(dm)
        
        if not (channel in self.incoming and self.incoming[channel]):
            return False

        if channel == "local":
            dm.content = _(u"Local message @ `{}`".format(self.player.location.pretty_print()))
            de.title = _("To Local @ `{}`").format(self.player.location.pretty_print())
        elif channel == "starsystem":
            dm.content = _(u"System wide message @ `{}`".format(self.player.star_system))
            de.title = _("To System @ `{}`").format(self.player.star_system)
        elif channel == "squadron":
            dm.content = _(u"Squadron message")
            de.title = _("To Squadron")
        elif channel == "squadronleaders":
            dm.content = _(u"Squadron Leaders message")
            de.title = _("To Squadron Leaders")
        dm.add_embed(de)
        return self.incoming[channel].send(dm)
    
    def __cmdrname_to_discord_color(self, name):
        saturation = [0.35, 0.5, 0.65]
        lightness = [0.35, 0.5, 0.65]
        
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

                
    def __process_outgoing(self, entry):
        channel = entry["To"]
        command_parts = entry["Message"].split(" ", 1)
        command = command_parts[0].lower()
        if command and command[0] == "!":
            if len(command_parts) < 2:
                return False

            if command == "!discord" and self.outgoing["broadcast"]:
                dm = EDRDiscordMessage()
                dm.content = _(u"Incoming broadcast")
                de = EDRDiscordEmbed()
                de.title = _("Channel `{}`").format(channel)
                de.description = " ".join(command_parts[1:])
                de.author = {
                    "name": self.player.name,
                    "url": "",
                    "icon_url": ""
                }
                de.timestamp = entry["timestamp"]
                de.color = self.__cmdrname_to_discord_color(self.player.name)
                dm.add_embed(de)
                de.footer = {
                    "text": "Message sent via ED Recon on behalf of Cmdr {}".format(self.player.name),
                    "icon_url": "https://lekeno.github.io/favicon-16x16.png"
                }
                
                return self.outgoing["broadcast"].send(dm)
            return False

        dm = EDRDiscordMessage()
        dm.content = ""
        de = EDRDiscordEmbed()
        de.title = _("Channel `{}`").format(channel)
        de.description = entry["Message"]
        de.author = {
            "name": self.player.name,
            "url": "",
            "icon_url": ""
        }
        de.timestamp = entry["timestamp"]
        de.color = self.__cmdrname_to_discord_color(self.player.name)
        de.footer = {
            "text": "Message sent via ED Recon on behalf of Cmdr {}".format(self.player.name),
            "icon_url": "https://lekeno.github.io/favicon-16x16.png"
        }
        dm.add_embed(de)
        
        if not channel in self.outgoing:
            return False
        
        #TODO content is different....
        return self.outgoing[channel].send(dm)