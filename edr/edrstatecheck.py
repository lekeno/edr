from edri18n import _, _c, _edr

class EDRBasicStateCheck(object):
    def __init__(self, states, allegiance = None):
        self.states = (state.lower() for state in states) if states else None
        self.allegiance = allegiance
        self.systems_counter = 0
        self.stations_counter = None
    
    def check_system(self, system):
        self.systems_counter = self.systems_counter + 1
        if not system:
            return False
        
        if not system.get('information', None):
            return False
        
        info = system['information']
        info['population'] = info.get('population', 0)
        
        if info['population'] < 1000000:
            return False

        return True

    def check_state(self, state):
        if not state or not self.states:
            return True
        return state.lower() in self.states

    def check_allegiance(self, allegiance):
        if not allegiance or not self.allegiance:
            return True
        return allegiance.lower() == self.allegiance.lower()

    def locations(self):
        return []

    def hint(self):
        return None


class EDRPharmaceuticalIsolatorsCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        #  - Specialist component developed during times of outbreak. Known to be salvaged from signal sources. 
        #  - Pharmaceutical isolators are used to extract and confine organic compounds from within a larger sample.
        super(EDRPharmaceuticalIsolatorsCheck, self).__init__(states=['Outbreak'])

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]

    def hint(self):
        return _(u"Found in systems under an 'Outbreak'. Greater chance in Independent, Alliance or Anarchy systems.")

class EDRImperialShieldingCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        # - Advanced component found in Imperial systems.
        # - Known to be salvaged from signal sources.
        # - Imperial shielding is an advanced form of shield management using proprietary technology.
        super(EDRImperialShieldingCheck, self).__init__(states=['None', 'Election'], allegiance='Empire')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]
    
    def hint(self):
        return _(u"Found in Empire systems with no state or an 'Election' state. Lower chance with 'Boom', 'War', 'Civic War' and 'Outbreak'.")

class EDRCoreDynamicsCompositesCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        # - Advanced component found in Federal systems. Known to be salvaged from signal sources. 
        # - Core Dynamics composites are a development by Core Dynamics providing increased protection over standard composites.
        super(EDRCoreDynamicsCompositesCheck, self).__init__(states=None, allegiance='Federation')

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Combat ships salvage')]

    def hint(self):
        return _(u"Found in Federal systems with no state or an 'Election' state. Lower chance with 'Boom', 'War', 'Civic War' and 'Outbreak'.")

class EDRProtoHeatRadiatorCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        # - Specialist component developed during economic boom. Known to be salvaged from signal sources. 
        # - Proto heat radiators use fluid transfer to move heat from a system.
        super(EDRProtoHeatRadiatorCheck, self).__init__(states=['Boom'], allegiance=None)

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]

    def hint(self):
        return _(u"Found in systems with a 'Boom' state. Greater chance in Independent or Alliance systems.")

class EDRProtoRadiolicAlloysCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        # - Specialist component developed during economic boom. Known to be salvaged from signal sources. 
        # - These advanced alloys use radiation to form complex materials. 
        super(EDRProtoRadiolicAlloysCheck, self).__init__(states=['Boom'], allegiance=None)

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]

    def hint(self):
        return _(u"Found in system with a 'Boom' state. Greater chance in Independent or Alliance systems.")

class EDRImprovisedComponentsCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        # - Specialist component used by factions in times of civil unrest. Known to be salvaged from signal sources. 
        # - These jury rigged components can fill in for crafted or manufactured components in a pinch.
        super(EDRImprovisedComponentsCheck, self).__init__(states=['Civil unrest'], allegiance=None)

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]

    def hint(self):
        return _(u"Found in system with a 'Civic unrest' state. Greater chance in Independent or Alliance systems.")

class EDRMilitaryGradeAlloysCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        # - Advanced component used by factions in times of war. Known to be salvaged from signal sources in systems in a state of civil war or war. 
        # - Military grade alloys provide an overall improved protection over standard alloys.
        super(EDRMilitaryGradeAlloysCheck, self).__init__(states=['War', 'Civil war'], allegiance=None)

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]
    
    def hint(self):
        return _(u"Found in systems at 'War' or 'Civic War'. Greater chance in Independent, Alliance or Anarchy systems.")

class EDRMilitarySupercapacitorsCheck(EDRBasicStateCheck):

    def __init__(self):
        super(EDRMilitarySupercapacitorsCheck, self).__init__(states=['War', 'Civil war'], allegiance=None)

    def locations(self):
        return [_(u'USS (high grade)'), _(u'Mission reward')]
    
    def hint(self):
        return _(u"Found in systems at 'War' or 'Civic War'. Greater chance in Independent, Alliance or Anarchy systems.")

class EDRExquisiteFocusCrystalsCheck(EDRBasicStateCheck):

    def __init__(self):
        # From Inara:
        # - Advanced component used by factions in times of war. Known to be salvaged from signal sources in systems in a state of civil war or war. 
        # - Military grade alloys provide an overall improved protection over standard alloys.
        super(EDRExquisiteFocusCrystalsCheck, self).__init__(states=['Boom'], allegiance=None)

    def locations(self):
        return [_(u'Mission reward')]
    
    def hint(self):
        return _(u"Greater chance in 'Boom' system state.")
