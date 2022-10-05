from __future__ import absolute_import
from subprocess import call

try:
    # for Python2
    import Tkinter as tk
    import ttk
except ImportError:
    # for Python3
    import tkinter as tk
    from tkinter import ttk

import sys
import config as EDMCConfig
from igmconfig import IGMConfig
import ttkHyperlinkLabel

from edri18n import _

class EntryWithPlaceholder(tk.Entry):
    def __init__(self, master=None, placeholder="type here", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.focus_in)
        self.bind("<FocusOut>", self.focus_out)

        self.show_placeholder()

    def show_placeholder(self):
        self.delete(0, tk.END)
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color
        
    def focus_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete(0, tk.END)
            self['fg'] = self.default_fg_color

    def focus_out(self, *args):
        if not self.get():
            self.show_placeholder()


class ToggledFrame(tk.Frame):

    def __init__(self, parent, label, status, show, callback_entry, *args, **options):
        conf = IGMConfig(config_file='config/igm_alt_config.v3.ini', user_config_file=['config/user_igm_alt_config.v3.ini', 'config/user_igm_alt_config.v2.ini'])
        theme=EDMCConfig.config.get_int('theme') # hat tip to ewanm89@
        if (theme):
            conf = IGMConfig(config_file='config/igm_alt_themed_config.v3.ini', user_config_file=['config/user_igm_alt_themed_config.v3.ini', 'config/user_igm_alt_themed_config.v2.ini'])
        
        fg = conf.rgb("status", "body")
        bg = conf.rgb("status", "fill")
        tk.Frame.__init__(self, parent, *args, **options)
        self.configure(background=bg)
        self.tk_setPalette(background=bg, foreground=fg, activeBackground=conf.rgb("status", "active_bg"), activeForeground=conf.rgb("status", "active_fg"))
        
        self.show = show
        
        self.grid(sticky="nsew")
        self.status_frame = tk.Frame(self)
        self.status_frame.configure(background=bg)
        self.status_frame.grid(row=0, column=0, sticky="ew")
        self.grid_columnconfigure(0, weight=1)
        
        self.sub_frame = tk.Frame(self, relief="flat", borderwidth=0)
        self.sub_frame.configure(background=bg)
        self.sub_frame.grid(row=1, column=0, sticky="nsew")
        
        separator = ttk.Separator(self.status_frame, orient=tk.HORIZONTAL)
        separator.grid(row=0, columnspan=3, sticky="ew")
        self.status_frame.grid_rowconfigure(0, weight=1)

        self.label = tk.Label(self.status_frame, text=label, foreground=conf.rgb("status", "label"), background=bg)
        self.label.grid(sticky="nw", row=1, column=0)
        self.status_ui = ttkHyperlinkLabel.HyperlinkLabel(self.status_frame, textvariable=status, foreground=fg, background=bg)
        self.status_ui.grid(sticky="ew", row=1, column=1)
        
        self.toggle_button = tk.Checkbutton(self.status_frame, width=2, text='+', command=self.toggle,
                                            variable=self.show, foreground=conf.rgb("status", "check"), background=bg)
        self.toggle_button.grid(sticky="e", row=1, column=2)
        
        self.input = EntryWithPlaceholder(self.status_frame, placeholder=_("Waiting for a game session..."))
        self.input.bind("<Return>", (lambda event: callback_entry(self.input.get())))
        self.input.grid(sticky="ew", row=2, column=0, columnspan=3)
        self.input.config(state='disabled')
        
        self.status_frame.grid_columnconfigure(2, weight=1)

    def toggle(self):
        if bool(self.show.get()):
            self.sub_frame.grid(row=1, column=0, sticky="nsew")
            self.sub_frame.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(1,weight=1)
            self.toggle_button.configure(text='-')
            self.status_frame.grid_columnconfigure(1, weight=1)
        else:
            self.sub_frame.grid_forget()
            self.grid_rowconfigure(0,weight=1)
            self.toggle_button.configure(text='+')
            self.status_frame.grid_columnconfigure(2, weight=1)
    
    def refresh_theme(self):
        self.status_frame.grid_propagate(False)
        conf = IGMConfig(config_file='config/igm_alt_config.v3.ini', user_config_file=['config/user_igm_alt_config.v3.ini', 'config/user_igm_alt_config.v2.ini'])
        theme=EDMCConfig.config.get_int('theme') # hat tip to ewanm89@
        if (theme):
            conf = IGMConfig(config_file='config/igm_alt_themed_config.v3.ini', user_config_file=['config/user_igm_alt_themed_config.v3.ini', 'config/user_igm_alt_themed_config.v2.ini'])
        
        fg = conf.rgb("status", "body")
        bg = conf.rgb("status", "fill")
        self.configure(background=bg)
        self.tk_setPalette(background=bg, foreground=fg, activeBackground=conf.rgb("status", "active_bg"), activeForeground=conf.rgb("status", "active_fg"))
        
        self.status_frame.configure(background=bg)
        self.sub_frame.configure(background=bg)
        self.label.configure(foreground=conf.rgb("status", "label"), background=bg)
        self.status_ui.configure(foreground=fg, background=bg)
        self.toggle_button.configure(foreground=conf.rgb("status", "check"), background=bg)


class EDRTogglingPanel(ToggledFrame):
    def __init__(self, status, show, callback_entry, parent=0):
        conf = IGMConfig(config_file='config/igm_alt_config.v3.ini', user_config_file=['config/user_igm_alt_config.v3.ini', 'config/user_igm_alt_config.v2.ini'])
        theme=EDMCConfig.config.get_int('theme') # hat tip to ewanm89@
        if (theme):
            conf = IGMConfig(config_file='config/igm_alt_themed_config.v3.ini', user_config_file=['config/user_igm_alt_themed_config.v3.ini', 'config/user_igm_alt_themed_config.v2.ini'])
        self.callback_entry = callback_entry
        ToggledFrame.__init__(self, parent, label="EDR:", status=status, show=show, callback_entry=self.__entry_process)
        self.bg_color = conf.rgb("general", "fill")
        self.fg_color = conf.rgb("general", "body")
        self.configure(background=self.bg_color)
        self.grid(sticky="nswe")
        self.output = tk.Text(self.sub_frame, width=conf.len("general", "body"), height=conf.body_rows("general"),
                                                bg=self.bg_color, fg=self.fg_color,
                                                wrap=tk.WORD, padx=4, borderwidth=0)
        scrollbar = ttk.Scrollbar(self.sub_frame, command=self.output.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')
        
        self.output.grid(row=0, column=0, sticky="nswe")
        self.output.config(state="disabled", yscrollcommand= scrollbar.set)
        self.output.bind("<1>", lambda event: self.output.focus_set())
        
        self.__configure_tags(conf)
        self.toggle()

    def enable_entry(self):
        self.input.config(state='normal')
        self.input.placeholder = _("Type EDR commands here or via the in-game chat.")
        self.input.show_placeholder()

    def disable_entry(self):
        self.input.placeholder = _("Waiting for a game session...")
        self.input.show_placeholder()
        self.input.config(state='disabled')

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
        self.output.config(state="normal")
        self.output.insert(1.0,u"\n", ("body_"+kind))
        body.reverse()
        for line in body:
            self.output.insert(1.0, line, ("body_"+kind))
            self.output.insert(1.0, u"\n", ("body_"+kind))
        self.output.insert(1.0, header, ("header_"+kind))
        self.output.insert(1.0, "\n", ("header_"+kind))
        self.output.config(state="disabled")
    
    def clear(self):
        self.output.config(state="normal")
        self.output.delete(1.0, tk.END)
        self.output.config(state="disabled")

    def __configure_tags(self, conf):
        kinds = ["sitrep", "intel", "warning", "notice", "help"]
        for kind in kinds:
            self.output.tag_configure("header_"+kind, foreground=conf.rgb(kind, "header"), background=conf.rgb("general", "fill"))
            self.output.tag_configure("body_"+kind, foreground=conf.rgb(kind, "body"), background=conf.rgb("general", "fill"))
    
    def refresh_theme(self):
        conf = IGMConfig(config_file='config/igm_alt_config.v3.ini', user_config_file=['config/user_igm_alt_config.v3.ini', 'config/user_igm_alt_config.v2.ini'])
        theme=EDMCConfig.config.get_int('theme') # hat tip to ewanm89@
        if (theme):
            conf = IGMConfig(config_file='config/igm_alt_themed_config.v3.ini', user_config_file=['config/user_igm_alt_themed_config.v3.ini', 'config/user_igm_alt_themed_config.v2.ini'])
        if sys.version_info.major == 2:
            super(EDRTogglingPanel, self).refresh_theme()
        else:
            super().refresh_theme()
        self.bg_color = conf.rgb("general", "fill")
        self.fg_color = conf.rgb("general", "body")
        self.configure(background=self.bg_color)
        self.output.configure(bg=self.bg_color, fg=self.fg_color)
        self.__configure_tags(conf)

    def __entry_process(self, command):
        if not command:
            return "break"
        
        if self.callback_entry(command):
            self.input.delete(0, tk.END)
            self.input.config(fg=self.fg_color)
        else:
            self.input.config(fg="red")
            self.notify(_("Unrecognized command"), [_("This doesn't appear to be a recognized command."), _("Please verify the prefix and syntax."), _("Use the !help command for further info.")])

        return "break"
