from edri18n import _, _c, _edr
import math

class EDRBasicStateCheck(object):
    def __init__(self):
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
        self.mandatory_states.add(state.lower())

    def optional_state(self, state):
        self.optional_states.add(state.lower())

    def forbidden_state(self, state):
        self.forbidden_states.add(state.lower())

    def mandatory_allegiance(self, allegiance):
        self.mandatory_allegiances.add(allegiance.lower())

    def optional_allegiance(self, allegiance):
        self.optional_allegiances.add(allegiance.lower())

    def forbidden_allegiance(self, allegiance):
        self.forbidden_allegiances.add(allegiance.lower())

    def mandatory_security(self, security):
        self.mandatory_security_levels.add(security.lower())

    def optional_security(self, security):
        self.optional_security_levels.add(security.lower())

    def grade_system(self, system):
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
        return []

    def hint(self):
        return None


class EDRPharmaceuticalIsolatorsCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRPharmaceuticalIsolatorsCheck, self).__init__()
        self.name = 'Pharmaceutical Isolators'
        self.mandatory_state('outbreak')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')
        self.optional_security('anarchy')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]

    def hint(self):
        return _(u"Found in systems under an 'Outbreak'. Greater chance in Independent, Alliance or Anarchy systems.")

class EDRImperialShieldingCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRImperialShieldingCheck, self).__init__()
        self.name = 'Imperial Shielding'
        self.mandatory_state('none')
        self.mandatory_state('election')
        self.mandatory_allegiance('empire')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]
    
    def hint(self):
        return _(u"Found in Empire systems with no state or an 'Election' state. Lower chance with 'Boom', 'War', 'Civic War' and 'Outbreak'.")

class EDRCoreDynamicsCompositesCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRCoreDynamicsCompositesCheck, self).__init__()
        self.name = 'Core Dynamics Composites'
        self.mandatory_state('none')
        self.mandatory_state('election')
        self.mandatory_allegiance('federation')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Combat ships salvage')]

    def hint(self):
        return _(u"Found in Federal systems with no state or an 'Election' state. Lower chance with 'Boom', 'War', 'Civic War' and 'Outbreak'.")

class EDRProtoLightAlloysCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRProtoLightAlloysCheck, self).__init__()
        self.name = 'Proto Light Alloys'
        self.mandatory_state('boom')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')

    def locations(self):
        return [_(u'USS (high grade)')]

    def hint(self):
        return _(u"Found in systems with a 'Boom' state. Greater chance in Independent or Alliance systems.")

class EDRProtoHeatRadiatorCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRProtoHeatRadiatorCheck, self).__init__()
        self.name = 'Proto Heat Radiator'
        self.mandatory_state('boom')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]

    def hint(self):
        return _(u"Found in systems with a 'Boom' state. Greater chance in Independent or Alliance systems.")

class EDRProtoRadiolicAlloysCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        # - Specialist component developed during economic boom. Known to be salvaged from signal sources. 
        # - These advanced alloys use radiation to form complex materials. 
        super(EDRProtoRadiolicAlloysCheck, self).__init__()
        self.name = 'Proto Radiolic Alloys'
        self.mandatory_state('boom')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]

    def hint(self):
        return _(u"Found in system with a 'Boom' state. Greater chance in Independent or Alliance systems.")

class EDRImprovisedComponentsCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRImprovisedComponentsCheck, self).__init__()
        self.name = 'Improvised Components'
        self.mandatory_state('civil unrest')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]

    def hint(self):
        return _(u"Found in system with a 'Civic unrest' state. Greater chance in Independent or Alliance systems.")

class EDRMilitaryGradeAlloysCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRMilitaryGradeAlloysCheck, self).__init__()
        self.name = 'Military Grade Alloy'
        self.mandatory_state('civil war')
        self.mandatory_state('war')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')
        self.optional_security('anarchy')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]
    
    def hint(self):
        return _(u"Found in systems at 'War' or 'Civic War'. Greater chance in Independent, Alliance or Anarchy systems.")

class EDRMilitarySupercapacitorsCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRMilitarySupercapacitorsCheck, self).__init__()
        self.name = 'Military Supercapacitors'
        self.mandatory_state('civil war')
        self.mandatory_state('war')
        self.optional_allegiance('independent')
        self.optional_allegiance('alliance')
        self.optional_security('anarchy')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]
    
    def hint(self):
        return _(u"Found in systems at 'War' or 'Civic War'. Greater chance in Independent, Alliance or Anarchy systems.")

class EDRExquisiteFocusCrystalsCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRExquisiteFocusCrystalsCheck, self).__init__()
        self.name = 'Exquisite Focus Crystals'
        self.mandatory_state('boom')

    def locations(self):
        return [_(u'Mission reward')]
    
    def hint(self):
        return _(u"Greater chance in 'Boom' system state.")

class EDRProprietaryCompositesCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRProprietaryCompositesCheck, self).__init__()
        self.name = 'Proprietary Composites'
        self.mandatory_state('election')
        self.mandatory_allegiance('empire')
        self.mandatory_allegiance('federal')

    def locations(self):
        return [_(u'USS (high grade)')]
    
    def hint(self):
        return _(u"Found in Empire and Federation system with an 'Election' state.")


class EDRDataminedWakeExceptionsCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRDataminedWakeExceptionsCheck, self).__init__()
        self.name = 'Datamined Wake Exceptions'
        self.mandatory_state('famine')

    def locations(self):
        return [_(u'Distribution Center (1000 LS of planetary orbits)')]
    
    def hint(self):
        return _(u"Captured from 'High Energy Wakes' with a wake scanner. Higher chance from 'Distribution Center' in systems with a 'Famine' state.")

class EDRPolymerCapacitorsCheck(EDRBasicStateCheck):
    def __init__(self):
        super(EDRPolymerCapacitorsCheck, self).__init__()
        self.name = 'Polymer Capacitors'
        self.optional_state('war')
        self.optional_state('civic war')
        self.mandatory_security('anarchy')

    def locations(self):
        return [_(u'USS (encoded emissions)'), _(u'Conflict Zone (military/authority)')]
    
    def hint(self):
        return _(u"Found in USS (encoded emissions) at Anarchy systems. Greater chances with systems at 'War' or 'Civic war'. Destroy military/authority ships in Combat Zone.")

class EDRThermicAlloysCheck(EDRBasicStateCheck):
    def __init__(self):
        super(EDRThermicAlloysCheck, self).__init__()
        self.name = 'Thermic Alloys'
        self.mandatory_state('war')
        self.mandatory_state('civic war')

    def locations(self):
        return [_(u'Conflict Zone (military/authority)'), _(u'Mission reward')]
    
    def hint(self):
        return _(u"Destroy military/authority ships in Combat Zone. Also a Mission Reward. Greater chances with systems at 'War' or 'Civic war'.")
