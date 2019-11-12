# coding= utf-8
import os
import sys

import igmconfig
import edrlog
import textwrap
from edri18n import _

EDRLOG = edrlog.EDRLog()

_overlay_dir = os.path.join(os.path.dirname(__file__).decode(sys.getfilesystemencoding()), u'EDMCOverlay')

if _overlay_dir not in sys.path:
    sys.path.append(_overlay_dir)

try:
    import edmcoverlay
except ImportError:
    raise Exception(str(sys.path))

import lrucache

class InGameMsg(object):   
    MESSAGE_KINDS = [ "intel", "warning", "sitrep", "notice", "help", "navigation"]

    def __init__(self):
        self._overlay = edmcoverlay.Overlay()
        self.cfg = {}
        self.general_config()
        self.must_clear = False
        for kind in self.MESSAGE_KINDS:
            self.message_config(kind)
        self.msg_ids = lrucache.LRUCache(1000, 60*15)

    def general_config(self):
        conf = igmconfig.IGMConfig()
        self.cfg["general"] = {
            "large" : {
                "h": conf.large_height(),
                "w": conf.large_width()
            },
            "normal" : {
                "h": conf.normal_height(),
                "w": conf.normal_width()
            }
        }


    def message_config(self, kind):
        conf = igmconfig.IGMConfig() 
        self.cfg[kind] = {
            "h": {
                "x": conf.x(kind, "header"),
                "y": conf.y(kind, "header"),
                "ttl": conf.ttl(kind, "header"),
                "rgb": conf.rgb(kind, "header"),
                "size": conf.size(kind, "header"),
                "len": conf.len(kind, "header"),
                "align": conf.align(kind, "header")
            },
            "b": {
                "x": conf.x(kind, "body"),
                "y": conf.y(kind, "body"),
                "ttl": conf.ttl(kind, "body"),
                "rgb": conf.rgb(kind, "body"),
                "size": conf.size(kind, "body"),
                "len": conf.len(kind, "body"),
                "align": conf.align(kind, "body"),
                "rows": conf.body_rows(kind),
                "cache": lrucache.LRUCache(conf.body_rows(kind), conf.ttl(kind, "body")),
                "last_row": 0
            }
        }
        if not conf.panel(kind):
            return
        self.cfg[kind]["panel"] = {
            "x": conf.x(kind, "panel"),
            "y": conf.y(kind, "panel"),
            "x2": conf.x2(kind, "panel"),
            "y2": conf.y2(kind, "panel"),
            "ttl": conf.ttl(kind, "panel"),
            "rgb": conf.rgb(kind, "panel"),
            "fill": conf.fill(kind, "panel")
        }


    def intel(self, header, details):
        self.__clear_if_needed()
        if "panel" in self.cfg["intel"]:
            self.__shape("intel", self.cfg["intel"]["panel"])
        self.__msg_header("intel", header)
        self.__msg_body("intel", details)

    def warning(self, header, details):
        self.__clear_if_needed()
        if "panel" in self.cfg["warning"]:
            self.__shape("warning", self.cfg["warning"]["panel"])
        self.__msg_header("warning", header)
        self.__msg_body("warning", details)

    def notify(self, header, details):
        self.__clear_if_needed()
        if "panel" in self.cfg["notice"]:
            self.__shape("notify", self.cfg["notify"]["panel"])
        self.__msg_header("notice", header)
        self.__msg_body("notice", details)
    
    def help(self, header, details):
        self.__clear_if_needed()
        if "panel" in self.cfg["help"]:
            self.__shape("help", self.cfg["help"]["panel"])
        self.__msg_header("help", header)
        self.__msg_body("help", details)
        self.must_clear = True

    def sitrep(self, header, details):
        self.__clear_if_needed()
        self.__clear_kind("sitrep")
        if "panel" in self.cfg["sitrep"]:
            self.__shape("sitrep", self.cfg["sitrep"]["panel"])
        self.__msg_header("sitrep", header)
        self.__msg_body("sitrep", details)

    def navigation(self, bearing, destination, distance=None, pitch=None):
        self.clear_navigation()
        if "panel" in self.cfg["navigation"]:
            self.__shape("navigation", self.cfg["navigation"]["panel"])
        header = u"› {:03} ‹     ↓ {:02} ↓".format(bearing, pitch) if pitch else u"> {:03} <".format(bearing)
        details = [destination.title] if destination.title else []
        if distance:
            details.append(_(u"Dis: {}km".format(int(distance))))
        details.append(_(u"Lat: {:.4f}".format(destination.latitude)))
        details.append(_(u"Lon: {:.4f}".format(destination.longitude)))
        self.__msg_header("navigation", header)
        self.__msg_body("navigation", details)

    def clear(self):
        for msg_id in self.msg_ids.keys():
            self.__clear(msg_id)
        self.msg_ids.reset()
        self.must_clear = False

    def clear_intel(self):
        self.__clear_kind("intel")
    
    def clear_sitrep(self):
        self.__clear_kind("sitrep")

    def clear_notice(self):
        self.__clear_kind("notice")
    
    def clear_warning(self):
        self.__clear_kind("warning")

    def clear_navigation(self):
        self.__clear_kind("navigation")

    def __clear_kind(self, kind):
        tag = "EDR-{}".format(kind)
        for msg_id in self.msg_ids.keys():
            if msg_id.startswith(tag):
                self.__clear(msg_id)
                self.msg_ids.evict(msg_id)

    def __clear_if_needed(self):
        if self.must_clear:
            self.clear()
    
    def __wrap_body(self, kind, lines):
        if not lines:
            return []
        chunked_lines = []
        rows = self.cfg[kind]["b"]["rows"]
        rows_per_line = max(1, rows / len(lines))
        bonus_rows = rows % len(lines)
        for line in lines:
            max_rows = rows_per_line
            if bonus_rows:
                max_rows += 1
            wrapped_text = self.__wrap_text(kind, "b", line, max_rows)
            if bonus_rows and wrapped_text == max_rows:
               bonus_rows -= 1
            chunked_lines.append(wrapped_text)
            if len(chunked_lines) >= rows:
                break
        return chunked_lines

    def __wrap_text(self, kind, part, text, max_rows):
        EDRLOG.log(u"text: {}".format(text), "DEBUG")
        if text is None:
            return None
        width = self.cfg[kind][part]["len"]
        wrapper = textwrap.TextWrapper(width=width, subsequent_indent="  ", break_on_hyphens=False)
        return wrapper.wrap(text)[:max_rows]

    def __adjust_x(self, kind, part, text):
        conf = self.cfg[kind][part]
        x = conf["x"]
        if conf["align"] == "center":
            w = self.cfg["general"][conf["size"]]["w"]
            text_w = len(text)*w
            return max(0,int(x-text_w/2.0))
        return x

    def __msg_header(self, kind, header, timeout=None):
        conf = self.cfg[kind]["h"]
        ttl = timeout if timeout else conf["ttl"]
        text = header[:conf["len"]]
        x = self.__adjust_x(kind, "h", text)
        EDRLOG.log(u"header={}, row={}, col={}, color={}, ttl={}, size={}".format(header, conf["y"], x, conf["rgb"], ttl, conf["size"]), "DEBUG")
        self.__display(kind, text, row=conf["y"], col=x, color=conf["rgb"], ttl=ttl, size=conf["size"])

    def __msg_body(self, kind, body, timeout=None):
        conf = self.cfg[kind]["b"]
        ttl = timeout if timeout else conf["ttl"]
        x = conf["x"]
        chunked_lines = self.__wrap_body(kind, body)
        
        for chunked_line in chunked_lines:
            if chunked_line is None:
                continue
            for chunk in chunked_line:
                row_nb = self.__best_body_row(kind, chunk)
                y = conf["y"] + row_nb * self.cfg["general"][conf["size"]]["h"]
                conf["cache"].set(row_nb, chunk)
                x = self.__adjust_x(kind, "b", chunk)
                EDRLOG.log(u"line={}, rownb={}, last_row={}, row={}, col={}, color={}, ttl={}, size={}".format(chunk, row_nb, conf["last_row"], y, x, conf["rgb"], ttl, conf["size"]), "DEBUG")
                self.__display(kind, chunk, row=y, col=x, color=conf["rgb"], size=conf["size"], ttl=ttl)
                self.__bump_body_row(kind)

    def __best_body_row(self, kind, text):
        rows = range(self.cfg[kind]["b"]["rows"])
        used_rows = []
        for row_nb in rows:
            cached = self.cfg[kind]["b"]["cache"].get(row_nb)
            used_rows.append(row_nb)
            if (cached is None or cached == text):
                return row_nb
        
        remaining_rows = (set(rows) - set(used_rows))
        if len(remaining_rows):
            return remaining_rows.pop()
        else:
            self.__bump_body_row(kind)
            return self.cfg[kind]["b"]["last_row"]

    def __bump_body_row(self, kind):
        self.cfg[kind]["b"]["last_row"] += 1
        if self.cfg[kind]["b"]["last_row"] > self.cfg[kind]["b"]["rows"]:
            self.cfg[kind]["b"]["last_row"] = 0


    def __display(self, kind, text, row, col, color="#dd5500", size="large", ttl=5):
        try:
            msg_id = "EDR-{}-{}".format(kind, row)
            self._overlay.send_message(msg_id, text, color, int(col), int(row), ttl=ttl, size=size)
            self.msg_ids.set(msg_id, ttl)
        except:
            EDRLOG.log(u"In-Game Message failed.", "ERROR")
            pass

    def __shape(self, kind, panel):
        try:
            shape_id = "EDR-shape-{}-{}-{}-{}-{}".format(kind, panel["x"], panel["y"], panel["x2"], panel["y2"])
            self._overlay.send_shape(shape_id, "rect", panel["rgb"], panel["fill"], panel["x"], panel["y"], panel["x2"], panel["y2"], ttl=panel["ttl"])
            self.msg_ids.set(shape_id, panel["ttl"])
        except:
            EDRLOG.log(u"In-Game Shape failed.", "ERROR")
            pass

    def __clear(self, msg_id):
        try:
            self._overlay.send_message(msg_id, "", "", 0, 0, 0, 0)
            self.msg_ids.evict(msg_id)
            self.__reset_caches()
        except:
            EDRLOG.log(u"In-Game Message failed to clear {}.".format(msg_id), "ERROR")
            pass
    
    def __reset_caches(self):
        for kind in self.MESSAGE_KINDS:
            self.cfg[kind]["b"]["cache"].reset()    

    def shutdown(self):
        # TODO self._overlay.shutdown() or something
        return
