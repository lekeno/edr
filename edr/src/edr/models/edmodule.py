import json
import re
import os

from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL


def load_power_data():
    try:
        path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')), 'data', 'modules_power_data.json')
        with open(path, 'r') as f:
            return json.loads(f.read())
    except Exception:
        EDR_LOG.warning("Failed to load modules_power_data.json")
        return {}

POWER_DATA = load_power_data()


class EDResistances:
    """
    Represents resistance stats for a module (hull/shield).
    """

    def __init__(self, thermal=0, kinetic=0, explosive=0, caustic=0):
        self.thermal = thermal
        self.kinetic = kinetic
        self.explosive = explosive
        self.caustic = caustic


class EDModule:
    """
    Represents a ship module in Elite Dangerous.
    """

    def __init__(self, module):
        self.power_draw = self._get_power_draw(module)
        self.power_generation = self._get_power_gen(module)
        self.priority = self._get_priority(module)
        self.cname = module["Item"].lower() if "Item" in module else None
        self.on = module.get("On", False)

    def update(self, module):
        """
        Update the module state from a new loadout event.
        Returns True if something meaningful changed.
        """
        prev_power_draw = self.power_draw
        prev_priority = self.priority
        prev_cname = self.cname
        prev_on = self.on

        EDR_LOG.debug(f"before: {prev_cname}, {prev_power_draw}, {prev_priority}, {prev_on}")

        self.power_draw = module["Power"] if "Power" in module else self._get_power_draw(module)
        self.priority = self._get_priority(module)
        self.cname = module["Item"].lower() if "Item" in module else None
        self.on = module.get("On", True)

        updated = (prev_power_draw != self.power_draw or
                   prev_priority != self.priority or
                   prev_cname != self.cname or
                   prev_on != self.on)
        
        if updated:
            EDR_LOG.debug(f"after: {self.cname}, {self.power_draw}, {self.priority}, {self.on}")
        return updated

    def is_valid(self):
        """Check if the module data is valid enough to use."""
        return not (self.priority is None or self.power_draw is None or self.cname is None)

    def generic_name(self):
        """Extract the generic name from the internal ID (e.g., removing grade/class)."""
        match = re.search('([a-zA-Z_]*)_size[0-9]_class[0-9](_[a-zA-Z_]*)?', self.cname)
        if match:
            return match.group(1)
        return self.cname

    def size_and_class(self):
        """Extract size and class from the internal ID."""
        match = re.search('[a-zA-Z_]*_size([0-9])_class([0-9])_[a-zA-Z_]*', self.cname)
        if match:
            return match.groups()
        return None

    def readable_name(self):
        """Return a human-readable name for common modules."""
        lut = {
            "int_hyperdrive": "FSD",
            "int_engine": "Thruster",
            "int_shieldgenerator": "Shield"
        }
        return lut.get(self.cname, self.cname)

    def is_shield(self):
        """Check if this module is a shield generator."""
        return self.cname.startswith('int_shieldgenerator')

    def is_prospector_drone_controller(self):
        """Check if this module is a prospector limpet controller."""
        return self.cname.startswith('int_dronecontrol_prospector')

    def is_drone_controller(self):
        """Check if this module is any type of limpet controller."""
        return self.cname.startswith('int_dronecontrol') or self.cname.startswith('int_multidronecontrol')

    def __repr__(self):
        return str(self.__dict__)

    @staticmethod
    def _get_power_draw(module):
        """Calculate power draw handling engineering modifiers and known base values."""
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        power_draw = None
        item = module["Item"].lower() if "Item" in module else None
        
        # Zero power draw items
        if item is None or item.startswith((
            'int_fueltank_', 'int_planetapproachsuite', 'int_passengercabin_', 
            'int_cargorack_', 'int_corrosionproof', 'int_hullreinforcement_', 
            'int_metaalloyhullreinforcement_', 'int_modulereinforcement_', 
            'int_detailedsurfacescanner_'
        )):
            power_draw = 0
            
        elif item in POWER_DATA:
            power_draw = POWER_DATA[item]["powerdraw"]
            
        elif item and item.startswith("modularcargobaydoor"):
            power_draw = 0.6
            
        elif item and not (
            item.startswith(('nameplate_', 'paintjob_', 'voicepack_', 'weaponcustomisation_', 
                           'enginecustomisation_', 'bobble_', 'decal_')) or 
            item.endswith(('_cockpit', '_armour_grade1', '_armour_grade2', 
                         '_armour_grade3', '_armour_mirrored', '_armour_reactive'))
        ):
            EDR_LOG.debug(f"unknown item: {item}")

        for modifier in modifiers:
            if modifier.get("Label", "").lower() != "powerdraw":
                continue
            power_draw = modifier["Value"]
        return power_draw

    @staticmethod
    def _get_priority(module):
        """Calculate power priority."""
        if module["Item"].lower().startswith('int_guardian') and 'Priority' not in module:
            # Guardian modules often have fixed priority/always on
            return 1
        return module["Priority"] + 1 if "Priority" in module else None

    @staticmethod
    def _get_power_gen(module):
        """Calculate power generation."""
        power_generation = 0
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        item = module["Item"].lower() if "Item" in module else None
        power_generation = POWER_DATA[item]["powergen"] if item in POWER_DATA else None
        for modifier in modifiers:
            if modifier.get("Label", "").lower() != "powercapacity":
                continue
            power_generation = modifier["Value"]
        return power_generation
