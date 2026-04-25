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
        self.hotkeys_path = edr_config_path('hotkeys.json')
        self.mappings = {}
        self.enabled = False
        self.load_mappings()

    def load_mappings(self):
        if not os.path.exists(self.hotkeys_path):
            EDR_LOG.info("No hotkeys.json found, using default empty mappings.")
            self.mappings = {}
            return

        try:
            with open(self.hotkeys_path, 'r') as f:
                self.mappings = json.load(f)
        except Exception as e:
            EDR_LOG.error(f"Failed to load hotkeys.json: {e}")
            self.mappings = {}

    def _save(self):
        try:
            with open(self.hotkeys_path, 'w') as f:
                json.dump(self.mappings, f, indent=2)
            return True
        except Exception as e:
            EDR_LOG.error(f"Failed to save hotkeys.json: {e}")
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
                    callback=self.hotkey_callback,
                    payload={"action_id": action_id}
                )
            )

    def hotkey_callback(self, payload=None, source="hotkey", hotkey=None):
        """
        The Bridge: Converts an Action ID into an application command execution.
        """
        if not payload:
            return

        action_id = payload.get("action_id")
        if action_id in self.mappings:
            command_str = self.mappings[action_id].get("command")
            if command_str:
                EDR_LOG.info(f"Hotkey triggered: {action_id} -> {command_str}")
                # Dispatch to main thread if necessary (EDRClient/EDRCommands call)
                # For now, calling directly as EDRClient.process_command
                self.edr_client.process_command(command_str)

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
        
        return self._save()

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
        
        return self._save()

    def clear_macro(self, slot):
        if not slot:
            return False
        
        action_id = f"edr.macro_{slot}"
        if action_id in self.mappings:
            del self.mappings[action_id]
            return self._save()
        return True

    def get_macros(self):
        macros = []
        for action_id, data in self.mappings.items():
            if action_id.startswith("edr.macro_"):
                slot = action_id[len("edr.macro_"):]
                macros.append(f"{slot}: {data['command']}")
        return macros

