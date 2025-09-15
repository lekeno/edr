import tkinter as tk
from tkinter import ttk

import myNotebook as notebook
import ttkHyperlinkLabel
from edrtogglingpanel import EDRTogglingPanel
from edri18n import _

class EDRClientUI(object):
    def __init__(self, edr_client, parent):
        self.edr_client = edr_client
        self.parent = parent
        self.ui = EDRTogglingPanel(self.edr_client._status, self.edr_client._visual_alt_feedback, self.edr_client.edrcommands.process, parent=self.parent)

    def app_ui(self):
        if self.ui is None:
            self.ui = EDRTogglingPanel(self.edr_client._status, self.edr_client._visual_alt_feedback, self.edr_client.edrcommands.process, parent=self.parent)
        
        self.ui.notify(_(u"Troubleshooting"), [
            _(u"If the overlay doesn't show up, try one of the following:"),
            _(u" - In E:D Market Connector: click on the File menu, then Settings, EDR, and select the Overlay checkbox."),
            _(u" - In Elite: go to graphics options, and select Borderless or Windowed."),
            _(u" - With Elite and EDR launched, check that EDMCOverlay.exe is running in the task manager."), 
            _(u"   If it's not running, then you may have to manually run it once (look in the plugins folder for 'EDMCOverlay.exe'."),
            _(u"If the overlay hurts your FPS, try turning VSYNC off in Elite's graphics options."),
            u"----",
            _("Join https://edrecon.com/discord for further technical support.")])
        return self.ui
    
    def refresh_theme(self):
        self.ui.refresh_theme()

    def enable_entry(self):
        self.ui.enable_entry()
    
    def disable_entry(self):
        self.ui.disable_entry()

    def notify(self, header, body):
        self.ui.notify(header, body)

    def help(self, header, body):
        self.ui.help(header, body)

    def clear(self):
        self.ui.clear()

    def intel(self, header, body):
        self.ui.intel(header, body)
    
    def sitrep(self, header, body):
        self.ui.sitrep(header, body)

    def warning(self, header, body):
        self.ui.warning(header, body)

    def nolink(self):
        self.ui.nolink()
        
    def link(self, link):
        self.ui.link(link)

    def prefs_ui(self, parent):
        frame = notebook.Frame(parent)
        frame.columnconfigure(1, weight=1)

        # Translators: this is shown in the preferences panel
        ttkHyperlinkLabel.HyperlinkLabel(frame, text=_(u"EDR website"), background=notebook.Label().cget('background'), url="https://edrecon.com", underline=True).grid(padx=10, sticky=tk.W)       
        ttkHyperlinkLabel.HyperlinkLabel(frame, text=_(u"EDR community"), background=notebook.Label().cget('background'), url="https://edrecon.com/discord", underline=True).grid(padx=10, sticky=tk.W)       

        # Translators: this is shown in the preferences panel
        notebook.Label(frame, text=_(u'Credentials')).grid(padx=10, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
        # Translators: this is shown in the preferences panel
        cred_frame = notebook.Frame(frame)
        cred_label_text = _(u'Log in with your EDR account for full access. {}')
        cred_label = notebook.Label(cred_frame, text=cred_label_text.format(""))
        cred_label.pack(side=tk.LEFT)
        # Translators: this is shown in the preferences panel, after a sentence saying "Log in with your EDR account for full access."
        apply_text = _(u"Apply for an account.")
        ttkHyperlinkLabel.HyperlinkLabel(cred_frame, text=apply_text, background=notebook.Label().cget('background'), url="https://edrecon.com/account", underline=True).pack(side=tk.LEFT)
        cred_frame.grid(padx=10, columnspan=2, sticky=tk.W)

        notebook.Label(frame, text=_(u"Email")).grid(padx=10, row=11, sticky=tk.W)
        notebook.EntryMenu(frame, textvariable=self.edr_client._email).grid(padx=10, row=11,
                                                             column=1, sticky=tk.EW)

        notebook.Label(frame, text=_(u"Password")).grid(padx=10, row=12, sticky=tk.W)
        notebook.EntryMenu(frame, textvariable=self.edr_client._password,
                       show=u'*').grid(padx=10, row=12, column=1, sticky=tk.EW)

        notebook.Label(frame, text=_(u'Broadcasts')).grid(padx=10, row=14, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
        notebook.Checkbutton(frame, text=_(u"Report crimes"),
                             variable=self.edr_client._crimes_reporting).grid(padx=10, row=16, sticky=tk.W)
        notebook.Label(frame, text=_("Redact my info in Sitreps")).grid(padx=10, row = 17, sticky=tk.W)
        choices = { _(u'Auto'),_(u'Always'),_(u'Never')}
        popupMenu = notebook.OptionMenu(frame, self.edr_client._anonymous_reports, self.edr_client.anonymous_reports, *choices)
        popupMenu.grid(padx=10, row=17, column=1, sticky=tk.EW)
        popupMenu["menu"].configure(background="white", foreground="black")

        notebook.Label(frame, text=_(u"Announce my Fleet Carrier's jump schedule")).grid(padx=10, row = 18, sticky=tk.W)
        choices = { _(u'Never'),_(u'Public'),_(u'Private'), _(u'Direct')}
        popupMenu = notebook.OptionMenu(frame, self.edr_client._fc_jump_psa, self.edr_client.fc_jump_psa, *choices, command=self.__toggle_fc_links)
        popupMenu.grid(padx=10, row=18, column=1, sticky=tk.EW)
        popupMenu["menu"].configure(background="white", foreground="black")
        self._private_fc_link = ttkHyperlinkLabel.HyperlinkLabel(frame, text=_(u"Configure your private channel (managed by EDR)"), background=notebook.Label().cget('background'), url="https://forms.gle/7pntJRpDgRBcbcfp8", underline=True)
        self._direct_fc_link = notebook.Label(frame, text=_(u"Configure your Fleet Carrier channel in config/user_config.ini"))
        self._private_fc_link.grid(padx=10, row=19, column=1, sticky=tk.EW)
        self._direct_fc_link.grid(padx=10, row=20, column=1, sticky=tk.EW)
        if self.edr_client.fc_jump_psa == _(u'Private'):
            self._direct_fc_link.grid_remove()
        elif self.edr_client.fc_jump_psa == _(u'Direct'):
            self._private_fc_link.grid_remove()
        else:
            self._private_fc_link.grid_remove()
            self._direct_fc_link.grid_remove()

        if self.edr_client.server.is_authenticated():
            if self.edr_client.is_anonymous():
                self.edr_client.status = _(u"authenticated (guest).")
            else:
                self.edr_client.status = _(u"authenticated.")
        else:
            self.edr_client.status = _(u"not authenticated.")

        # Translators: this is shown in the preferences panel as a heading for feedback options (e.g. overlay, audio cues)
        notebook.Label(frame, text=_(u"EDR Feedback:")).grid(padx=10, row=21, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
        
        notebook.Label(frame, text=_(u"Overlay")).grid(padx=10, row = 23, sticky=tk.W)
        choices = { _(u"Enabled"),_(u"Standalone (for VR or multi-display)"), _(u'Disabled')}
        popupMenu = notebook.OptionMenu(frame, self.edr_client._visual_feedback_type, self.edr_client.visual_feedback_type, *choices)
        popupMenu.grid(padx=10, row=23, column=1, sticky=tk.EW)
        popupMenu["menu"].configure(background="white", foreground="black")
        
        notebook.Checkbutton(frame, text=_(u"Sound"),
                             variable=self.edr_client._audio_feedback).grid(padx=10, row=24, sticky=tk.W)

        return frame

    def __toggle_fc_links(self, choice):
        if choice == _(u'Private'):
            self._private_fc_link.grid()
            self._direct_fc_link.grid_remove()
        elif choice == _(u"Direct"):
            self._direct_fc_link.grid()
            self._private_fc_link.grid_remove()
        else:
            self._private_fc_link.grid_remove()
            self._direct_fc_link.grid_remove()
