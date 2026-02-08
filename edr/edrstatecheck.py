from edri18n import _, _c, _edr  # EDR_INTERNAL
import math


class EDRBasicStateCheck:
    """
    Base class for system state and allegiance checks.
    """
    def __init__(self):
        """
        Initialize the check definition.
        """
        self.mandatory_states = set()
        self.optional_states = set()
        self.forbidden_states = set()
        self.mandatory_allegiances = set()
        self.optional_allegiances = set()
        self.forbidden_allegiances = set()
        self.mandatory_security_levels = set()
        self.optional_security_levels = set()
        self.systems_counter = 0
        self.stations_counter = None
        self.name = None

    def mandatory_state(self, state):
        """
        Add a mandatory state.

        Args:
            state (str): System state name.
        """
        self.mandatory_states.add(state.lower())

    def optional_state(self, state):
        """
        Add an optional state.

        Args:
            state (str): System state name.
        """
        self.optional_states.add(state.lower())

    def forbidden_state(self, state):
        """
        Add a forbidden state.

        Args:
            state (str): System state name.
        """
        self.forbidden_states.add(state.lower())

    def mandatory_allegiance(self, allegiance):
        """
        Add a mandatory allegiance.

        Args:
            allegiance (str): Allegiance name.
        """
        self.mandatory_allegiances.add(allegiance.lower())

    def optional_allegiance(self, allegiance):
        """
        Add an optional allegiance.

        Args:
            allegiance (str): Allegiance name.
        """
        self.optional_allegiances.add(allegiance.lower())

    def forbidden_allegiance(self, allegiance):
        """
        Add a forbidden allegiance.

        Args:
            allegiance (str): Allegiance name.
        """
        self.forbidden_allegiances.add(allegiance.lower())

    def mandatory_security(self, security):
        """
        Add a mandatory security level.

        Args:
            security (str): Security level.
        """
        self.mandatory_security_levels.add(security.lower())

    def optional_security(self, security):
        """
        Add an optional security level.

        Args:
            security (str): Security level.
        """
        self.optional_security_levels.add(security.lower())

    def grade_system(self, system):
        """
        Grade a system based on population, security, and other criteria.

        Args:
            system (dict): System info.

        Returns:
            int: Grade (higher is better).
        """
        grade = 1
        self.systems_counter = self.systems_counter + 1
        if not system:
            return 0

        if not system.get('information', None):
            return 0

        info = system['information']
        info['population'] = info.get('population', 0)

        if info['population'] >= 1000000:
            grade += 1 * int(max(3, math.log10(info['population'] / 100000)))

        info['security'] = info.get('security', '')
        if self.mandatory_security_levels:
            if not info['security']:
                return 0
            elif info['security'].lower() not in self.mandatory_security_levels:
                return 0

        if self.optional_security_levels:
            if info['security'].lower() in self.optional_security_levels:
                grade += 1

        return grade

    def grade_state(self, state):
        """
        Grade a state based on mandatory, forbidden, and optional states.

        Args:
            state (str): System state.

        Returns:
            int: Grade.
        """
        grade = 1
        cstate = state.lower() if state else state
        if self.mandatory_states:
            if cstate not in self.mandatory_states:
                return 0

        if self.forbidden_states:
            if cstate in self.forbidden_states:
                return 0

        if self.optional_states and cstate in self.optional_states:
            grade += 1

        return grade

    def grade_allegiance(self, allegiance):
        """
        Grade an allegiance based on mandatory, forbidden, and optional allegiances.

        Args:
            allegiance (str): Allegiance.

        Returns:
            int: Grade.
        """
        grade = 1
        callegiance = allegiance.lower() if allegiance else allegiance
        if self.mandatory_allegiances:
            if callegiance not in self.mandatory_allegiances:
                return 0

        if self.forbidden_allegiances:
            if callegiance in self.forbidden_allegiances:
                return 0

        if self.optional_allegiances and callegiance in self.optional_allegiances:
            grade += 1

        return grade

    def locations(self):
        """
        Return list of locations where item can be found.

        Returns:
            list: List of location strings.
        """
        return []

    def hint(self):
        """
        Return a hint about where to find the item.

        Returns:
            str: Hint text.
        """
        return None



class EDRPharmaceuticalIsolatorsCheck(EDRBasicStateCheck):
    """
    Check for Pharmaceutical Isolators.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Pharmaceutical Isolators'
        self.mandatory_state('outbreak')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')
        self.optional_security('anarchy')

    def locations(self):
        """
        Return locations for Pharmaceutical Isolators.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)'), _('Mission reward')]

    def hint(self):
        """
        Return hint for finding Pharmaceutical Isolators.

        Returns:
            str: Hint text.
        """
        return _("Found in systems under an 'Outbreak'. Greater chance in Independent, Alliance or Anarchy systems.")


class EDRImperialShieldingCheck(EDRBasicStateCheck):
    """
    Check for Imperial Shielding.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Imperial Shielding'
        self.mandatory_state('none')
        self.mandatory_state('election')
        self.mandatory_allegiance('empire')

    def locations(self):
        """
        Return locations for Imperial Shielding.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)'), _('Mission reward')]

    def hint(self):
        """
        Return hint for finding Imperial Shielding.

        Returns:
            str: Hint text.
        """
        return _("Found in Empire systems with no state or an 'Election' state. Lower chance with 'Boom', 'War', 'Civil War' and 'Outbreak'.")


class EDRCoreDynamicsCompositesCheck(EDRBasicStateCheck):
    """
    Check for Core Dynamics Composites.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Core Dynamics Composites'
        self.mandatory_state('none')
        self.mandatory_state('election')
        self.mandatory_allegiance('federation')

    def locations(self):
        """
        Return locations for Core Dynamics Composites.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)'), _('Combat ships salvage')]

    def hint(self):
        """
        Return hint for finding Core Dynamics Composites.

        Returns:
            str: Hint text.
        """
        return _("Found in Federal systems with no state or an 'Election' state. Lower chance with 'Boom', 'War', 'Civil War' and 'Outbreak'.")


class EDRProtoLightAlloysCheck(EDRBasicStateCheck):
    """
    Check for Proto Light Alloys.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Proto Light Alloys'
        self.mandatory_state('boom')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')

    def locations(self):
        """
        Return locations for Proto Light Alloys.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)')]

    def hint(self):
        """
        Return hint for finding Proto Light Alloys.

        Returns:
            str: Hint text.
        """
        return _("Found in systems with a 'Boom' state. Greater chance in Independent or Alliance systems.")


class EDRProtoHeatRadiatorCheck(EDRBasicStateCheck):
    """
    Check for Proto Heat Radiators.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Proto Heat Radiators'
        self.mandatory_state('boom')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')

    def locations(self):
        """
        Return locations for Proto Heat Radiators.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)'), _('Mission reward')]

    def hint(self):
        """
        Return hint for finding Proto Heat Radiators.

        Returns:
            str: Hint text.
        """
        return _("Found in systems with a 'Boom' state. Greater chance in Independent or Alliance systems.")


class EDRProtoRadiolicAlloysCheck(EDRBasicStateCheck):
    """
    Check for Proto Radiolic Alloys.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        # From Inara:
        # - Specialist component developed during economic boom. Known to be salvaged from signal sources.
        # - These advanced alloys use radiation to form complex materials.
        super().__init__()
        self.name = 'Proto Radiolic Alloys'
        self.mandatory_state('boom')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')

    def locations(self):
        """
        Return locations for Proto Radiolic Alloys.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)'), _('Mission reward')]

    def hint(self):
        """
        Return hint for finding Proto Radiolic Alloys.

        Returns:
            str: Hint text.
        """
        return _("Found in system with a 'Boom' state. Greater chance in Independent or Alliance systems.")


class EDRImprovisedComponentsCheck(EDRBasicStateCheck):
    """
    Check for Improvised Components.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Improvised Components'
        self.mandatory_state('civil unrest')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')

    def locations(self):
        """
        Return locations for Improvised Components.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)'), _('Mission reward')]

    def hint(self):
        """
        Return hint for finding Improvised Components.

        Returns:
            str: Hint text.
        """
        return _("Found in system with a 'Civil unrest' state. Greater chance in Independent or Alliance systems.")


class EDRMilitaryGradeAlloysCheck(EDRBasicStateCheck):
    """
    Check for Military Grade Alloys.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Military Grade Alloy'
        self.mandatory_state('civil war')
        self.mandatory_state('war')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')
        self.optional_security('anarchy')

    def locations(self):
        """
        Return locations for Military Grade Alloys.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)'), _('Mission reward')]

    def hint(self):
        """
        Return hint for finding Military Grade Alloys.

        Returns:
            str: Hint text.
        """
        return _("Found in systems at 'War' or 'Civil War'. Greater chance in Independent, Alliance or Anarchy systems.")


class EDRMilitarySupercapacitorsCheck(EDRBasicStateCheck):
    """
    Check for Military Supercapacitors.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Military Supercapacitors'
        self.mandatory_state('civil war')
        self.mandatory_state('war')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')
        self.optional_security('anarchy')

    def locations(self):
        """
        Return locations for Military Supercapacitors.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)'), _('Mission reward')]

    def hint(self):
        """
        Return hint for finding Military Supercapacitors.

        Returns:
            str: Hint text.
        """
        return _("Found in systems at 'War' or 'Civil War'. Greater chance in Independent, Alliance or Anarchy systems.")


class EDRExquisiteFocusCrystalsCheck(EDRBasicStateCheck):
    """
    Check for Exquisite Focus Crystals.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Exquisite Focus Crystals'
        self.mandatory_state('boom')

    def locations(self):
        """
        Return locations for Exquisite Focus Crystals.

        Returns:
            list: List of location strings.
        """
        return [_('Mission reward')]

    def hint(self):
        """
        Return hint for finding Exquisite Focus Crystals.

        Returns:
            str: Hint text.
        """
        return _("Greater chance in 'Boom' system state.")


class EDRProprietaryCompositesCheck(EDRBasicStateCheck):
    """
    Check for Proprietary Composites.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Proprietary Composites'
        self.mandatory_state('election')
        self.mandatory_allegiance('empire')
        self.mandatory_allegiance('federal')

    def locations(self):
        """
        Return locations for Proprietary Composites.

        Returns:
            list: List of location strings.
        """
        return [_('USS (high grade)')]

    def hint(self):
        """
        Return hint for finding Proprietary Composites.

        Returns:
            str: Hint text.
        """
        return _("Found in Empire and Federation system with an 'Election' state.")


class EDRDataminedWakeExceptionsCheck(EDRBasicStateCheck):
    """
    Check for Datamined Wake Exceptions.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Datamined Wake Exceptions'
        self.mandatory_state('famine')

    def locations(self):
        """
        Return locations for Datamined Wake Exceptions.

        Returns:
            list: List of location strings.
        """
        return [_('Distribution Center (1000 LS of planetary orbits)')]

    def hint(self):
        """
        Return hint for finding Datamined Wake Exceptions.

        Returns:
            str: Hint text.
        """
        return _("Captured from 'High Energy Wakes' with a wake scanner. Higher chance from 'Distribution Center' in systems with a 'Famine' state.")


class EDRPolymerCapacitorsCheck(EDRBasicStateCheck):
    """
    Check for Polymer Capacitors.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Polymer Capacitors'
        self.optional_state('war')
        self.optional_state('civil war')
        self.mandatory_security('anarchy')

    def locations(self):
        """
        Return locations for Polymer Capacitors.

        Returns:
            list: List of location strings.
        """
        return [_('USS (encoded emissions)'), _('Conflict Zone (military/authority)')]

    def hint(self):
        """
        Return hint for finding Polymer Capacitors.

        Returns:
            str: Hint text.
        """
        return _("Found in USS (encoded emissions) at Anarchy systems. Greater chances with systems at 'War' or 'Civil war'. Destroy military/authority ships in Combat Zone.")


class EDRThermicAlloysCheck(EDRBasicStateCheck):
    """
    Check for Thermic Alloys.
    """
    def __init__(self):
        """
        Initialize the check.
        """
        super().__init__()
        self.name = 'Thermic Alloys'
        self.mandatory_state('war')
        self.mandatory_state('civil war')

    def locations(self):
        """
        Return locations for Thermic Alloys.

        Returns:
            list: List of location strings.
        """
        return [_('Conflict Zone (military/authority)'), _('Mission reward')]

    def hint(self):
        """
        Return hint for finding Thermic Alloys.

        Returns:
            str: Hint text.
        """
        return _("Destroy military/authority ships in Combat Zone. Also a Mission Reward. Greater chances with systems at 'War' or 'Civil war'.")
