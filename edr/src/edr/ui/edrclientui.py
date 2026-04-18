import tkinter as tk
from tkinter import ttk

try:
    import myNotebook as notebook
except ImportError:
    notebook = None
try:
    import ttkHyperlinkLabel
except ImportError:
    ttkHyperlinkLabel = None
from .edrtogglingpanel import EDRTogglingPanel
from edr.core.edri18n import _

class EDRClientUI:
    """
    User Interface Controller for EDR.
    Manages the overlay, menus, and user notifications.
    """

    def __init__(self, edr_client, parent):
        """
        Initialize EDRClientUI.

        Args:
            edr_client (EDRClient): The EDR client instance.
            parent (object): The parent UI object (e.g. from EDMC).
        """
        self.edr_client = edr_client
        self.parent = parent
        self.ui = EDRTogglingPanel(
            self.edr_client._status,
            self.edr_client._visual_alt_feedback,
            self.edr_client.edrcommands.process,
            parent=self.parent
        )

        self.ui.notify(_("Troubleshooting"), [
            _("If the overlay doesn't show up, try one of the following:"),
            _(" - In E:D Market Connector: click on the File menu, then Settings, EDR, and select the Overlay checkbox."),
            _(" - In Elite: go to graphics options, and select Borderless or Windowed."),
            _(" - With Elite and EDR launched, check that EDMCOverlay.exe is running in the task manager."),
            _("   If it's not running, then you may have to manually run it once (look in the plugins folder for 'EDMCOverlay.exe'."),
            _("If the overlay hurts your FPS, try turning VSYNC off in Elite's graphics options."),
            "----",
            _("Join https://edrecon.com/discord for further technical support.")
        ])

    def app_ui(self):
        """Returns the main UI panel."""
        return self.ui

    def refresh_theme(self):
        """Refreshes the UI theme/styling."""
        self.ui.refresh_theme()

    def enable_entry(self):
        """Enables text entry on the UI."""
        self.ui.enable_entry()

    def disable_entry(self):
        """Disables text entry on the UI."""
        self.ui.disable_entry()

    def notify(self, header, body):
        """Displays a notification with header and body text."""
        self.ui.notify(header, body)

    def help(self, header, body):
        """Displays help content."""
        self.ui.help(header, body)

    def clear(self):
        """Clears the UI display."""
        self.ui.clear()

    def intel(self, header, body):
        """Displays intel information."""
        self.ui.intel(header, body)

    def sitrep(self, header, body):
        """Displays situation report."""
        self.ui.sitrep(header, body)

    def warning(self, header, body):
        """Displays a warning."""
        self.ui.warning(header, body)

    def nolink(self):
        """Clears any active links."""
        self.ui.nolink()

    def link(self, link):
        """Sets an active link."""
        self.ui.link(link)

    def prefs_ui(self, parent):
        """
        Builds and returns the preferences settings panel (frame).
        Used by EDMC to display plugin settings.
        """
        frame = notebook.Frame(parent)
        frame.columnconfigure(1, weight=1)

        # Translators: this is shown in the preferences panel
        ttkHyperlinkLabel.HyperlinkLabel(
            frame,
            text=_("EDR website"),
            background=notebook.Label().cget('background'),
            url="https://edrecon.com",
            underline=True
        ).grid(padx=10, sticky=tk.W)

        ttkHyperlinkLabel.HyperlinkLabel(
            frame,
            text=_("EDR community"),
            background=notebook.Label().cget('background'),
            url="https://edrecon.com/discord",
            underline=True
        ).grid(padx=10, sticky=tk.W)

        # Translators: this is shown in the preferences panel
        notebook.Label(frame, text=_('Credentials')).grid(padx=10, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)

        # Translators: this is shown in the preferences panel
        cred_frame = notebook.Frame(frame)
        cred_label_text = _('Log in with your EDR account for full access. {}')
        cred_label = notebook.Label(cred_frame, text=cred_label_text.format(""))
        cred_label.grid(row=0, column=0, sticky=tk.W)

        # Translators: this is shown in the preferences panel, after a sentence saying "Log in with your EE.DR account for full access."
        apply_text = _("Apply for an account.")
        ttkHyperlinkLabel.HyperlinkLabel(
            cred_frame,
            text=apply_text,
            background=notebook.Label().cget('background'),
            url="https://edrecon.com/account",
            underline=True
        ).grid(row=0, column=1, sticky=tk.W)
        cred_frame.grid(padx=10, columnspan=2, sticky=tk.W)

        notebook.Label(frame, text=_("Email")).grid(padx=10, row=11, sticky=tk.W)
        notebook.EntryMenu(frame, textvariable=self.edr_client._email).grid(padx=10, row=11, column=1, sticky=tk.EW)

        notebook.Label(frame, text=_("Password")).grid(padx=10, row=12, sticky=tk.W)
        notebook.EntryMenu(
            frame,
            textvariable=self.edr_client._password,
            show='*'
        ).grid(padx=10, row=12, column=1, sticky=tk.EW)

        notebook.Label(frame, text=_('Broadcasts')).grid(padx=10, row=14, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)
        
        notebook.Checkbutton(
            frame,
            text=_("Report crimes"),
            variable=self.edr_client._crimes_reporting
        ).grid(padx=10, row=16, sticky=tk.W)

        notebook.Label(frame, text=_("Redact my info in Sitreps")).grid(padx=10, row=17, sticky=tk.W)
        choices = {_('Auto'), _('Always'), _('Never')}
        popupMenu = notebook.OptionMenu(
            frame,
            self.edr_client._anonymous_reports,
            self.edr_client.anonymous_reports,
            *choices
        )
        popupMenu.grid(padx=10, row=17, column=1, sticky=tk.EW)
        popupMenu["menu"].configure(background="white", foreground="black")

        notebook.Label(frame, text=_("Announce my Fleet Carrier's jump schedule")).grid(padx=10, row=18, sticky=tk.W)
        choices = {_('Never'), _('Public'), _('Private'), _('Direct')}
        popupMenu = notebook.OptionMenu(
            frame,
            self.edr_client._fc_jump_psa,
            self.edr_client.fc_jump_psa,
            *choices,
            command=self.__toggle_fc_links
        )
        popupMenu.grid(padx=10, row=18, column=1, sticky=tk.EW)
        popupMenu["menu"].configure(background="white", foreground="black")

        self._private_fc_link = ttkHyperlinkLabel.HyperlinkLabel(
            frame,
            text=_("Configure your private channel (managed by EDR)"),
            background=notebook.Label().cget('background'),
            url="https://forms.gle/7pntJRpDgRBcbcfp8",
            underline=True
        )
        self._direct_fc_link = notebook.Label(frame, text=_("Configure your Fleet Carrier channel in config/user_config.ini"))
        self._private_fc_link.grid(padx=10, row=19, column=1, sticky=tk.EW)
        self._direct_fc_link.grid(padx=10, row=20, column=1, sticky=tk.EW)

        if self.edr_client.fc_jump_psa == _('Private'):
            self._direct_fc_link.grid_remove()
        elif self.edr_client.fc_jump_psa == _('Direct'):
            self._private_fc_link.grid_remove()
        else:
            self._private_fc_link.grid_remove()
            self._direct_fc_link.grid_remove()

        if self.edr_client.server.is_authenticated():
            if self.edr_client.is_anonymous():
                self.edr_client.status = _("authenticated (guest).")
            else:
                self.edr_client.status = _("authenticated.")
        else:
            self.edr_client.status = _("not authenticated.")

        # Translators: this is shown in the preferences panel as a heading for feedback options (e.g. overlay, audio cues)
        notebook.Label(frame, text=_("EDR Feedback:")).grid(padx=10, row=21, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)

        notebook.Label(frame, text=_("Overlay")).grid(padx=10, row=23, sticky=tk.W)
        choices = {_("Enabled"), _("Standalone (for VR or multi-display)"), _('Disabled')}
        popupMenu = notebook.OptionMenu(
            frame,
            self.edr_client._visual_feedback_type,
            self.edr_client.visual_feedback_type,
            *choices
        )
        popupMenu.grid(padx=10, row=23, column=1, sticky=tk.EW)
        popupMenu["menu"].configure(background="white", foreground="black")

        notebook.Checkbutton(
            frame,
            text=_("Sound"),
            variable=self.edr_client._audio_feedback
        ).grid(padx=10, row=24, sticky=tk.W)
        
        notebook.Label(frame, text=_("Features")).grid(padx=10, row=25, sticky=tk.W)
        ttk.Separator(frame, orient=tk.HORIZONTAL).grid(columnspan=2, padx=10, pady=2, sticky=tk.EW)

        notebook.Label(frame, text=_("Nb of top planets on a honk")).grid(padx=10, row = 27, sticky=tk.W)
        choices = { _("5"), _("10"), _("15"), _("All")}
        popupMenu = notebook.OptionMenu(
            frame, 
            self.edr_client._top_planets_count_in_system_report, 
            self.edr_client.top_planets_count_in_system_report, 
            *choices
        )
        popupMenu.grid(padx=10, row=27, column=1, sticky=tk.EW)
        popupMenu["menu"].configure(background="white", foreground="black")

        return frame

    def __toggle_fc_links(self, choice):
        """
        Topic toggle handler for Fleet Carrier links.

        Args:
            choice (str): The selected option.
        """
        if choice == _('Private'):
            self._private_fc_link.grid()
            self._direct_fc_link.grid_remove()
        elif choice == _("Direct"):
            self._direct_fc_link.grid()
            self._private_fc_link.grid_remove()
        else:
            self._private_fc_link.grid_remove()
            self._direct_fc_link.grid_remove()
