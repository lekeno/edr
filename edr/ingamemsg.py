import os
import sys

import Tkinter as tk
from config import config
import edrlog

EDRLOG = edrlog.EDRLog()

_thisdir = os.path.abspath(os.path.dirname(__file__))
_overlay_dir = os.path.join(_thisdir, "EDMCOverlay")
if _overlay_dir not in sys.path:
    print "adding {} to sys.path".format(_overlay_dir)
    sys.path.append(_overlay_dir)

try:
    import edmcoverlay
except ImportError:
    print sys.path
    raise Exception(str(sys.path))

import lrucache

class InGameMsg(object):
    VIRTUAL_WIDTH = 1280 #EDMCOverlay's virtual width
    VIRTUAL_HEIGHT = 960 #EDMCOverlay's virtual height
    
    LARGE_HEIGHT = 28
    LARGE_WIDTH = 7

    NORMAL_HEIGHT = 18
    NORMAL_WIDTH = 4

    WARNING_ROW = 50
    INFO_WARNING_ROW = WARNING_ROW + LARGE_HEIGHT
    WARNING_TIMEOUT = 20
    
    NOTICE_ROW = 500
    INFO_NOTICE_ROW = NOTICE_ROW + LARGE_HEIGHT

    INFO_NB_ROWS = 8

    def __init__(self):
        self._overlay = edmcoverlay.Overlay()
        self.info_notice_row = self.INFO_NOTICE_ROW
        self.info_warning_cache = lrucache.LRUCache(self.INFO_NB_ROWS, self.WARNING_TIMEOUT)
        self.iw_last_row_used = 0

        tmp = config.get("EDRVisualNormalWidth")
        self._normal_width = tk.DoubleVar(value=self.NORMAL_WIDTH if (tmp is None) else float(tmp))
        
        tmp = config.get("EDRVisualLargeWidth")
        self._large_width = tk.DoubleVar(value=self.LARGE_WIDTH if (tmp is None) else float(tmp))

        if self._normal_width == 0.0:
            self.normal_width = self.NORMAL_WIDTH
        
        if self._large_width == 0.0:
            self.large_width = self.LARGE_WIDTH


    @property
    def normal_width(self):
        return self._normal_width.get()

    @normal_width.setter
    def normal_width(self, new_width):
        self._normal_width.set(new_width)
        config.set("EDRVisualNormalWidth", str(new_width))
        

    @property
    def large_width(self):
        return self._large_width.get()

    @large_width.setter
    def large_width(self, new_width):
        self._large_width.set(new_width)
        config.set("EDRVisualLargeWidth", str(new_width))


    def notify(self, text, ttl=12):
        self.display(text, row=self.NOTICE_ROW, col=max(0,int(self.VIRTUAL_WIDTH/2.0-len(text)*self.large_width)), color="#dd5500", ttl=ttl)


    def warn(self, text):
        self.display(text, row=self.WARNING_ROW, col=max(0,int(self.VIRTUAL_WIDTH/2.0-len(text)*self.large_width)), color="red", ttl=self.WARNING_TIMEOUT, size="large")


    def info_warning(self, lines):
        for line in lines:
            row_nb = self.best_warning_row(line)
            self.iw_last_row_used = self.INFO_WARNING_ROW + row_nb * self.NORMAL_HEIGHT
            self.display(line, row=self.iw_last_row_used, col=max(0,int(self.VIRTUAL_WIDTH/2.0-len(line)*self.normal_width)), color="#ffffff", size="normal", ttl=self.WARNING_TIMEOUT)
            self.info_warning_cache.set(row_nb, line)


    def info_notify(self, lines, ttl=10):
        self.info_notice_row = self.INFO_NOTICE_ROW
        for line in lines:
            self.display(line, row=self.info_notice_row, col=max(0,int(self.VIRTUAL_WIDTH/2.0-len(line)*self.normal_width)), color="#ffffff", size="normal", ttl=ttl)
            self.bump_notice_row()


    def bump_warning_row(self):
        self.iw_last_row_used += 1
        if self.iw_last_row_used > self.INFO_NB_ROWS:
            self.iw_last_row_used = 0

    
    def bump_notice_row(self):
        self.info_notice_row += self.NORMAL_HEIGHT
        if self.info_notice_row > (self.INFO_NOTICE_ROW + self.NORMAL_HEIGHT * 8):
            self.info_notice_row = self.INFO_NOTICE_ROW


    def best_warning_row(self, text):
        rows = range(self.INFO_NB_ROWS)
        used_rows = []
        for row_nb in rows:
            cached = self.info_warning_cache.get(row_nb)
            used_rows.append(row_nb)
            if (cached is None or cached == text):
                return row_nb
        
        remaining_rows = (set(rows) - set(used_rows))
        if len(remaining_rows):
            return remaining_rows.pop()
        else:
            self.bump_warning_row()
            return self.iw_last_row_used


    def display(self, text, row, col, color="#dd5500", size="large", ttl=5):
        try:
            msgid = "EDR-{}".format(row) 
            self._overlay.send_message(msgid, text, color, col, row, ttl=ttl, size=size)
        except:
            EDRLOG.log(u"In-Game Message failed.", "ERROR")
            pass

    def shutdown(self):
        # TODO self._overlay.shutdown() or something
        return
