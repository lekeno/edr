import json
import requests
from datetime import datetime
from binascii import crc32
from numbers import Number

from edri18n import _
from edrconfig import EDRUserConfig 
from edrafkdetector import EDRAfkDetector

#import backoff # TODO

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
            self.files.append({"file": f.read(), "filename":name)


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
        self.timestamp = datetime.now().isoformat()


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
        #self.backoff = backoff.Backoff(u"Discord"),

    def send_text(self, text):
        if not self.webhook_url:
            return False
        #if self.backoff.throttled():
        #    return False
    
        message = DiscordSimpleMessage(text)
        payload_json = message.json()
        resp = EDRDiscordWebhook.SESSION.post(self.webhook_url, json=payload_json)
        return self.__check_response(resp)

    def send(self, discord_message):
        if not self.webhook_url:
            return False
        #if self.backoff.throttled():
        #    return False
    
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
            #self.backoff.reset()
            pass
        elif response.status_code in [429, 500]:
            #self.backoff.throttle()
            pass

        return response.status_code in [200, 204]

class EDRDiscordIntegration(object):
    # TODO pass the player itself since that would be handy to show system, location etc.
    def __init__(self, player):
        self.player = player
        self.afk_detector = EDRAfkDetector()
        user_config = EDRUserConfig()
        self.afk_wh = EDRDiscordWebhook(user_config.discord_afk_webhook())
        self.broadcast_wh = EDRDiscordWebhook(user_config.discord_broadcast_webhook())
        self.squadron_wh = EDRDiscordWebhook(user_config.discord_squadron_webhook())
        self.squadron_leaders_wh = EDRDiscordWebhook(user_config.discord_squadron_leaders_webhook())
        self.screenshot_wh = EDRDiscordWebhook(user_config.discord_screenshot_webhook())

    def process(self, entry):
        self.afk_detector.process(entry)

        if entry["event"] == "ReceiveText":
            return self.__process_incoming(entry)
        elif entry["event"] == "SendText":
            return self.__process_outgoing(entry)
        elif entry["event"] == "Screenshot" and self.screenshot_wh:
            return self.__process_screenshot(entry)
        return False

    def __process_incoming(self, entry):
        if entry.get("Channel", None) in ["player", "friend"] and self.afk_detector.is_afk() and self.afk_wh: # TODO verify the friend thing
            dm = EDRDiscordMessage()
            dm.content = _(u"Direct message received while AFK")
            dm.timestamp = entry["timestamp"]
            de = EDRDiscordEmbed()
            de.title = _("To Cmdr `{}`").format(self.player.name)
            de.description = entry["Message"]
            de.author = {
                "name": entry["From"],
                "url": "",
                "icon_url": ""
            }
            de.color = self.__cmdrname_to_discord_color(entry["From"])
            dm.add_embed(de)
            return self.afk_wh.send(dm)
        # TODO other: report my target?

        return False
    
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
        # TODO simplify
        if self.squadron_leaders_wh and entry["To"] == "squadleaders":
            dm = EDRDiscordMessage()
            dm.content = _(u"Squadron Leaders message")
            dm.timestamp = entry["timestamp"]
            de = EDRDiscordEmbed()
            de.title = _("Channel `{}`").format(entry["To"])
            de.description = entry["Message"]
            de.author = {
                "name": self.player.name,
                "url": "",
                "icon_url": ""
            }
            de.color = self.__cmdrname_to_discord_color(self.player.name)
            dm.add_embed(de)
            return self.broadcast_wh.send(dm)

        if self.squadron_wh and entry["To"] == "squadron":
            dm = EDRDiscordMessage()
            dm.content = _(u"Squadron message")
            dm.timestamp = entry["timestamp"]
            de = EDRDiscordEmbed()
            de.title = _("Channel `{}`").format(entry["To"])
            de.description = entry["Message"]
            de.author = {
                "name": self.player.name,
                "url": "",
                "icon_url": ""
            }
            de.color = self.__cmdrname_to_discord_color(self.player.name)
            dm.add_embed(de)
            return self.broadcast_wh.send(dm)
        
        command_parts = entry["Message"].split(" ", 1)
        command = command_parts[0].lower()
        if not command:
            return False

        if not command[0] == "!" or len(command_parts) < 2:
            return False
    
        if command == "!discord":
            if self.broadcast_wh:
                dm = EDRDiscordMessage()
                dm.content = _(u"Incoming broadcast")
                dm.timestamp = entry["timestamp"]
                de = EDRDiscordEmbed()
                de.title = _("Channel `{}`").format(entry["To"])
                de.description = " ".join(command_parts[1:])
                de.author = {
                    "name": self.player.name,
                    "url": "",
                    "icon_url": ""
                }
                de.color = self.__cmdrname_to_discord_color(self.player.name)
                dm.add_embed(de)
                return self.broadcast_wh.send(dm)
        # TODO other
        return False

    def __process_screenshot(self, entry):
        """ { 
                "timestamp":"2018-01-17T09:48:26Z", "event":"Screenshot",
                "Filename":"_Screenshots/Screenshot_0024.bmp", "Width":1440, "Height":900,
                "System":"Nuenets", "Body":"Nuenets C 2", "Latitude":-60.799900, "Longitude":-74.059799,
                "Heading":39, "Altitude":27502.876953 
            } 
        """
        filename = entry.get("Filename", None)
        w = entry.get("Width", 0)
        h = entry.get("Height", 0)
        system = entry.get("System", "Unknown")
        body = entry.get("Body", "")
        lat = entry.get("Latitude", None)
        lon = entry.get("Longitude", None)
        heading = entry.get("Heading", None)
        altitude = entry.get("Altitude", None)

        if not filename or w == 0 or h == 0:
            return False

        dm = EDRDiscordMessage()
        dm.content = _(u"Screenshot")
        dm.timestamp = entry["timestamp"]
        de = EDRDiscordEmbed()
        de.title = _("Screenshot from `{}`").format("{}, {}".format(system, body) if body else system)
        if not (latitude is None or longitude is None):
            parts = [
                _("Latitude:     {}").format(lat),
                _("Longitude:    {}").format(lon)
                 
            ]
            # "{: <12}{: >6}".format("latitude:", "{:.2f}".format(142.1))
            if not(heading is None or altitude is None):
                parts.append(_("Heading:      {}").fornat(heading))
                parts.append(_("Altitude:     {}").fornat(altitude))
            de.description = "```\n{}\n```".format("\n".join(parts))
        de.author = {
            "name": self.player.name,
            "url": "",
            "icon_url": ""
        }
        de.color = self.__cmdrname_to_discord_color(self.player.name)
        dm.add_embed(de)
        return self.screenshot_wh.send(dm)