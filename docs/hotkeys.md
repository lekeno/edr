## Design Doc: EDMCHotkeys Integration for EDR

**Dependency:** [EDMCHotkeys](https://github.com/SweetJonnySauce/EDMCHotkeys)

### 1. Objective
Enable EDR users to trigger features via keyboard shortcuts. This reduces the need to manually type commands in the in-game chat interface during high-intensity gameplay (e.g., combat or time-sensitive events).

---

### 2. Architecture: The "Bridge" Pattern
To avoid exposing internal methods or duplicating logic, the integration treats a hotkey press as a **virtual chat event**.

* **Input:** EDMCHotkeys intercepts a keypress and executes a callback in EDR.
* **Bridge:** The callback identifies the associated command string (e.g., `!traffic`).
* **Execution:** EDR passes this string to its existing command processor as if it were received from the standard game logs.

---

### 3. Configuration & Persistence
EDR follows a tiered configuration pattern to ensure human readability and flexibility.

#### A. Global Settings (`user_configs.ini`)
A new section handles the high-level toggle. It defaults to `True` in the plugin's base config.
```ini
[EDMCHotkeys]
enabled = True
```

#### B. Mapping Storage (`hotkeys.json`)
Hotkey mappings (Action ID → Command) are stored in JSON to handle complex strings and custom labels.

```json
{
  "edr.slot1": {
    "label": "Ganker Search",
    "command": "!intel \"CMDR Braben\""
  },
  "edr.slot2": {
    "label": "EDR Macro 2",
    "command": "!traffic"
  }
}
```

---

### 4. Feature Set

#### I. Pre-defined Actions
EDR registers a set of standard actions (e.g., Traffic, Intel, Ping) with EDMCHotkeys upon startup. These appear in the EDMCHotkeys settings menu for physical key binding.

#### II. In-Game Macro Management (The `!macro` command)
Users manage "Hotkey Slots" via chat to decouple command logic from physical key assignment.

* **Syntax:** `!macro [set|clear|list|show|name] [slot_number] [optional_command/name]`
* **Logic for set:** Captures the specified `optional_command` or the last successful command (prefixed with `!`, `?`, `#`, `-`, or `@`) and assigns it to the slot.
* **Logic for show:** `!macro show [slot_number]` displays the command currently assigned to that slot.
* **Logic for name:** `!macro name [slot_number] [name]` sets a custom label for the slot. The name must be a single alphanumeric word (requires EDMC restart to show in EDMCHotkeys).
* **Logic for clear:** `!macro clear [slot_number]` removes the mapping for that slot.
* **Logic for list:** `!macro list` displays all currently programmed macro slots and their commands.

**Persistence:** Changes are written immediately to `config/hotkeys.json`.


---

### 5. Technical Implementation (Python)

#### Callback & Registration
EDR implements an `EDRHotkeyManager` that bridges EDMCHotkeys actions to the EDR command processor.

```python
# edr/src/edr/controllers/edrhotkeys.py
import ExternalHotkeyPlugin as ehp

class EDRHotkeyManager(object):
    def register(self):
        if not ehp: return

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
        action_id = payload.get("action_id") if payload else None
        if action_id in self.mappings:
            command_str = self.mappings[action_id].get("command")
            self.edr_client.process_command(command_str)

# edr/load.py
def plugin_start():
    EDR_CLIENT.apply_config() # This triggers EDR_CLIENT.hotkey_manager.register()
```

---

### 6. Alternatives Considered
* **Direct Function Mapping:** Rejected. Mapping keys directly to internal methods would create a rigid API surface and bypass the validation present in the command processor.
* **Simulated Keypresses:** Rejected. Simulating keys to "type" into the game chat is fragile, prone to focus-loss errors, and intrusive to the user experience.