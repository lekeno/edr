import os
import json
from edr.core.edrlog import EDR_LOG
from edr.core.edrconfig import EDR_CONFIG
from edr.utils.edrpath import edr_config_path

try:
    import EDMCHotkeys as ehp
except ImportError:
    ehp = None

class EDRHotkeyManager(object):
    def __init__(self, edr_client):
        self.edr_client = edr_client
        self.config = EDR_CONFIG
        self.canonical_hotkeys_path = edr_config_path('hotkeys.json')
        self.user_hotkeys_path = edr_config_path('user_hotkeys.v1.json')
        self.mappings = {}
        self.enabled = False
        self.load_mappings()

    def load_mappings(self):
        self.enabled = True
        self.mappings = {
            "edr.macro_1": {"label": "Target Intel", "command": "!who"},
            "edr.macro_2": {"label": "Sitrep", "command": "!sitrep"},
            "edr.macro_3": {"label": "Tag Outlaw", "command": "#!"},
            "edr.macro_4": {"label": "Clear Overlay", "command": "!clear"}
        }

        # Load Canonical Mappings
        if os.path.exists(self.canonical_hotkeys_path):
            try:
                with open(self.canonical_hotkeys_path, 'r') as f:
                    data = json.load(f)
                    if "mappings" in data:
                        self.enabled = data.get("enabled", True)
                        self.mappings.update(data.get("mappings", {}))
                    else:
                        self.mappings.update(data)
            except Exception as e:
                EDR_LOG.error(f"Failed to load canonical hotkeys.json: {e}")

        # Override with User Mappings
        if os.path.exists(self.user_hotkeys_path):
            try:
                with open(self.user_hotkeys_path, 'r') as f:
                    data = json.load(f)
                    if "mappings" in data:
                        self.enabled = data.get("enabled", self.enabled)
                        self.mappings.update(data.get("mappings", {}))
                    else:
                        self.mappings.update(data)
            except Exception as e:
                EDR_LOG.error(f"Failed to load user_hotkeys.v1.json: {e}")

    def _save(self):
        try:
            with open(self.user_hotkeys_path, 'w') as f:
                data = {
                    "enabled": self.enabled,
                    "mappings": self.mappings
                }
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            EDR_LOG.error(f"Failed to save user_hotkeys.v1.json: {e}")
            return False

    def save_mappings(self):
        return self._save()


    def register(self):
        if not ehp:
            EDR_LOG.info("EDMCHotkeys not found. Hotkey integration disabled.")
            return

        if not self.enabled:
            EDR_LOG.info("Hotkey integration is disabled via configuration.")
            return

        EDR_LOG.info("Registering hotkeys with EDMCHotkeys.")
        for action_id, data in self.mappings.items():
            ehp.register_action(
                ehp.Action(
                    id=action_id,
                    label=data.get("label", action_id),
                    plugin="EDRecon",
                    callback=self.make_callback(action_id)
                )
            )

    def make_callback(self, action_id):
        """
        The Bridge: Generates a callback that converts an Action ID into an application command execution.
        """
        def callback(payload=None, source="hotkey", hotkey=None):
            if action_id in self.mappings:
                command_str = self.mappings[action_id].get("command")
                if command_str:
                    EDR_LOG.info(f"Hotkey triggered: {action_id} -> {command_str}")
                    # Dispatch to main thread if necessary (EDRClient/EDRCommands call)
                    # For now, calling directly as EDRClient.process_command
                    self.edr_client.process_command(command_str)
        return callback

    def update_macro(self, slot, command, label=None):
        if not slot:
            return False
        
        action_id = f"edr.macro_{slot}"
        if action_id not in self.mappings:
            self.mappings[action_id] = {
                "label": label if label else f"Macro Slot {slot}",
                "command": command
            }
        else:
            self.mappings[action_id]["command"] = command
            if label:
                self.mappings[action_id]["label"] = label
        
        success = self._save()
        if success:
            self.register()
        return success

    def update_label(self, slot, label):
        if not slot or not label:
            return False
        
        action_id = f"edr.macro_{slot}"
        if action_id not in self.mappings:
            self.mappings[action_id] = {
                "label": label,
                "command": ""
            }
        else:
            self.mappings[action_id]["label"] = label
        
        success = self._save()
        if success:
            self.register()
        return success

    def clear_macro(self, slot):
        if not slot:
            return False
        
        action_id = f"edr.macro_{slot}"
        if action_id in self.mappings:
            self.mappings[action_id] = {"label": "Cleared", "command": ""}
            success = self._save()
            if success:
                # Re-registering doesn't unregister, but we should at least save.
                # Currently EDMCHotkeys doesn't expose an unregister API, but saving is enough.
                self.register()
            return success
        return True

    def get_macros(self):
        macros = []
        for action_id, data in self.mappings.items():
            if action_id.startswith("edr.macro_"):
                slot = action_id[len("edr.macro_"):]
                macros.append(f"{slot}: {data['command']}")
        return macros

