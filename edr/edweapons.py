class EDDamageFractions:
    """
    Represents damage distribution across different types.
    """
    def __init__(self, absolute=0.0, explosive=0.0, kinetic=0.0, thermal=0.0, caustic=0.0):
        self.absolute = absolute
        self.explosive = explosive
        self.kinetic = kinetic
        self.thermal = thermal
        self.caustic = caustic

    def apply(self, damage):
        """
        Apply fractions to a total damage value.
        
        :param damage: Total damage amount.
        :return: Dictionary of damage by type.
        """
        return {
            "absolute": damage * self.absolute,
            "explosive": damage * self.explosive,
            "kinetic": damage * self.kinetic,
            "thermal": damage * self.thermal,
            "caustic": damage * self.caustic,
        }


class EDWeapon:
    """
    Base class for Elite Dangerous weapons.
    """
    def __init__(self):
        # TODO make this a child of EDModule, reflect powerdraw etc.
        self.damage = 0
        self.enhanced_damage = 0
        self.dps = 0
        self.enhanced_dps = 0
        self.fractions = EDDamageFractions()
        self.ammo_multiplier = 0
        self.temp_multiplier = 0
        self.weapon_temp_pct = 0
        self.enabled = True  # TODO take into account actual state
    
    def update_from(self, module):
        """Update weapon stats from a loadout module."""
        engineering = module.get("Engineering", {})
        modifiers = engineering.get("Modifiers", [])
        for m in modifiers:
            if m.get("Label", "") == "Damage" and "Value" in m:
                self.damage = m["OriginalValue"]
                self.enhanced_damage = m["Value"]
            elif m.get("Label", "") == "DamagePerSecond" and "Value" in m:
                self.dps = m["OriginalValue"]
                self.enhanced_dps = m["Value"]
            elif m.get("ExperimentalEffect", "") == "special_thermal_conduit":
                self.temp_multiplier = 0.6

    def basic_ammo(self):
        """Set ammo type to basic (no bonus)."""
        self.ammo_multiplier = 0.0

    def standard_ammo(self):
        """Set ammo type to standard (+15% damage)."""
        self.ammo_multiplier = 0.15

    def premium_ammo(self):
        """Set ammo type to premium (+30% damage)."""
        self.ammo_multiplier = 0.3

    def temperature_percent(self, temp_pct):
        """Set specific temperature percentage for thermal conduit calculations."""
        self.weapon_temp_pct = temp_pct
        
    def damage_per_shot(self):
        """Calculate damage per shot considering ammo and thermal conduit."""
        premium_bonus = self.damage * self.ammo_multiplier
        temp_multiplier = 0
        if self.weapon_temp_pct >= 1.5:
            temp_multiplier = self.temp_multiplier
        elif self.weapon_temp_pct > 0.9:
            temp_multiplier = (self.weapon_temp_pct - 0.9) / (1.5 - 0.9) * self.temp_multiplier

        damage = self.enhanced_damage or self.damage
        damage = damage * (1.0 + temp_multiplier) + premium_bonus
        return self.fractions.apply(damage)


class EDPlasmaAcc4A(EDWeapon):
    def __init__(self):
        super().__init__()
        self.damage = 125.2
        self.fractions = EDDamageFractions(0.6, 0.0, 0.2, 0.2)


class EDPlasmaAcc3A(EDWeapon):
    def __init__(self):
        super().__init__()
        self.damage = 83.4
        self.fractions = EDDamageFractions(0.6, 0.0, 0.2, 0.2)


class EDPlasmaAcc2A(EDWeapon):
    def __init__(self):
        super().__init__()
        self.damage = 54.3
        self.fractions = EDDamageFractions(0.6, 0.0, 0.2, 0.2)


class EDRailGun2B(EDWeapon):
    def __init__(self):
        super().__init__()
        self.damage = 41.5
        self.fractions = EDDamageFractions(0.0, 0.0, 1.0/3.0, 2.0/3.0)


class EDRailGun1D(EDWeapon):
    def __init__(self):
        super().__init__()
        self.damage = 23.3
        self.fractions = EDDamageFractions(0.0, 0.0, 1.0/3.0, 2.0/3.0)


class EDWeaponFactory:
    """
    Factory for creating EDWeapon instances from module names.
    """
    __module_classes = {
        "plasmaaccelerator_fixed_huge": EDPlasmaAcc4A,
        "plasmaaccelerator_fixed_large": EDPlasmaAcc3A,
        "plasmaaccelerator_fixed_medium": EDPlasmaAcc2A,
        "railgun_fixed_medium": EDRailGun2B,
        "railgun_fixed_small": EDRailGun1D,
    }

    @staticmethod
    def normalize_module_name(name):
        """Normalize module name strings from journal events."""
        normalized = name.lower()
        
        # suffix _name or _name; is not used in loadout or afmurepair events 
        if normalized.endswith("_name"):
            useless_suffix_length = len("_name")
            normalized = normalized[:-useless_suffix_length]
        elif normalized.endswith("_name;"):
            useless_suffix_length = len("_name;")
            normalized = normalized[:-useless_suffix_length]

        if normalized.startswith("$"):
            normalized = normalized[1:]

        # just get rid of prefixes because sometimes int_ becomes ext_ depending on the event
        if normalized.startswith(("int_", "ext_", "hpt_")):
            normalized = normalized[4:]
        return normalized

    @staticmethod
    def from_internal_name(internal_name):
        """Create a weapon instance from its internal name."""
        cname = EDWeaponFactory.normalize_module_name(internal_name)
        if cname in EDWeaponFactory.__module_classes:
            weapon = EDWeaponFactory.__module_classes[cname]()
            return weapon
        return None

    @staticmethod
    def from_module(module):
        """Create a weapon instance from a valid loadout module dictionary."""
        internal_name = module.get("Item", "N/A")
        cname = EDWeaponFactory.normalize_module_name(internal_name)
        if cname in EDWeaponFactory.__module_classes:
            weapon = EDWeaponFactory.__module_classes[cname]()
            weapon.update_from(module)
            return weapon
        return None
