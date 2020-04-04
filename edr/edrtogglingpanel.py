from __future__ import absolute_import

import Tkinter as tk
import ttk
from igmconfig import IGMConfig
import ttkHyperlinkLabel

class ToggledFrame(tk.Frame):

    def __init__(self, parent, label, status, show, *args, **options):
        conf = IGMConfig(config_file='config/igm_alt_config.v3.ini', user_config_file=['config/user_igm_alt_config.v3.ini', 'config/user_igm_alt_config.v2.ini'])
        tk.Frame.__init__(self, parent, *args, **options)
        fg = conf.rgb("status", "body")
        bg = conf.rgb("status", "fill")
        self.tk_setPalette(background=bg, foreground=fg, activeBackground=conf.rgb("status", "active_bg"), activeForeground=conf.rgb("status", "active_fg"))

        self.show = show
        self.title_frame = tk.Frame(self)
        self.title_frame.pack(fill="x", expand=1)

        ttk.Separator(self.title_frame, orient=tk.HORIZONTAL).pack(fill="x", expand=1)
        tk.Label(self.title_frame, text=label, foreground=conf.rgb("status", "label")).pack(side="left", fill="x", expand=0, anchor="w")
        self.status_ui = ttkHyperlinkLabel.HyperlinkLabel(self.title_frame, textvariable=status, foreground=fg, background=bg)
        self.status_ui.pack(side="left", fill="x", expand=0, anchor="w")
        
        self.toggle_button = tk.Checkbutton(self.title_frame, width=2, text='+', command=self.toggle,
                                            variable=self.show, foreground=conf.rgb("status", "check"))
        self.toggle_button.pack(side="right", expand=1, anchor="e")

        self.sub_frame = tk.Frame(self, relief="flat", borderwidth=0)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.pack(fill="x", expand=1)
            self.toggle_button.configure(text='-')
        else:
            self.sub_frame.forget()
            self.toggle_button.configure(text='+')

class EDRTogglingPanel(ToggledFrame):
    def __init__(self, status, show, parent=0):
        conf = IGMConfig(config_file='config/igm_alt_config.v3.ini', user_config_file=['config/user_igm_alt_config.v3.ini', 'config/user_igm_alt_config.v2.ini'])
        ToggledFrame.__init__(self, parent, label="EDR:", status=status, show=show)
        self.pack(fill="x", expand=1, pady=2, padx=2, anchor="n")
        self.output = tk.Text(self.sub_frame, width=conf.len("general", "body"), height=conf.body_rows("general"),
                                                background=conf.rgb("general", "fill"), foreground=conf.rgb("general", "body"),
                                                wrap=tk.WORD, padx=4, borderwidth=0)
        self.output.pack(fill="x", expand=1)

        self.__configure_tags(conf)
        self.toggle()

    def nolink(self):
        self.status_ui.url = None
        self.status_ui.underline = False

    def link(self, url):
        self.status_ui.underline = True
        self.status_ui.url = url

    def sitrep(self, header, body):
        self.__push_message("sitrep", header, body)

    def intel(self, header, body):
        self.__push_message("intel", header, body)

    def warning(self, header, body):
        self.__push_message("warning", header, body)
    
    def notify(self, header, body):
        self.__push_message("notice", header, body)
    
    def help(self, header, body):
        self.__push_message("help", header, body)

    def __push_message(self, kind, header, body):
        self.output.insert(1.0,u"\n", ("body_"+kind))
        body.reverse()
        for line in body:
            self.output.insert(1.0, line, ("body_"+kind))
            self.output.insert(1.0, u"\n", ("body_"+kind))
        self.output.insert(1.0, header, ("header_"+kind))
        self.output.insert(1.0, "\n", ("header_"+kind))
    
    def clear(self):
        self.output.delete(1.0, tk.END)

    def __configure_tags(self, conf):
        kinds = ["sitrep", "intel", "warning", "notice", "help"]
        for kind in kinds:
            self.output.tag_configure("header_"+kind, foreground=conf.rgb(kind, "header"))
            self.output.tag_configure("body_"+kind, foreground=conf.rgb(kind, "body"))
        