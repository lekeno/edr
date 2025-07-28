
from edri18n import _, _c, _edr
from edrsysstacheck import EDRSystemStationCheck, EDRApexSystemStationCheck
from edtime import EDTime


class EDRStationServiceCheck(EDRSystemStationCheck):

    def __init__(self, service):
        super(EDRStationServiceCheck, self).__init__()
        self.service = service
        self.name = service
        self.hint = None

    def check_station(self, station):
        if not super(EDRStationServiceCheck, self).check_station(station):
            return False

        if not station.get('otherServices', None):
            return False
        
        return self.service in station['otherServices']

    def is_service_availability_ambiguous(self, station):
        if "odyssey" in station.get("type", "").lower():
            return self.service not in ["Refuel","Repair","Contacts","Missions"] # TODO possibly too strict? confirmed: IFactors
        if "planetary" in station.get("type", "").lower():
            return True # TODO not sure what's up but since Odyssey release, the planetary port/outpost don't seem to have I.Factors anymore :/
        return False
    
class EDRStationFacilityCheck(EDRSystemStationCheck):

    def __init__(self, facility):
        super(EDRStationFacilityCheck, self).__init__()
        lut = {'shipyard': 'haveShipyard', 'market': 'haveMarket', 'outfitting': 'haveOutfitting'}
        self.has_facility = lut[facility.lower()] if facility.lower() in lut else None
        self.name = facility
        self.hint = None


    def check_station(self, station):
        if not super(EDRStationFacilityCheck, self).check_station(station):
            return False

        if not self.has_facility:
            return True

        return station.get(self.has_facility, False)

class EDRStagingCheck(EDRSystemStationCheck):

    def __init__(self, max_distance):
        super(EDRStagingCheck, self).__init__()
        self.max_distance = max_distance
        self.name = _(u"Staging station")
        self.hint = None

    def check_system(self, system):
        if not super(EDRStagingCheck, self).check_system(system):
            return False
        
        return system.get('distance', 1) >= 0 and system.get('distance', self.max_distance + 1) <= self.max_distance

    def check_station(self, station):
        if not super(EDRStagingCheck, self).check_station(station):
            return False

        if station.get("type", "") == "Fleet Carrier":
            return False

        if not station.get('otherServices', False):
            return False
        
        if not station.get('haveShipyard', False):
            return False

        if not station.get('haveOutfitting', False):
            return False

        if not (all(service in station['otherServices'] for service in ['Restock', 'Refuel', 'Repair'])):
            return False

        return True

class EDRStationRRRCheck(EDRSystemStationCheck):

    def __init__(self, max_distance, max_sc_distance):
        super(EDRStationRRRCheck, self).__init__()
        self.max_distance = max_distance
        self.max_sc_distance = max_sc_distance
        self.name = _(u"Station with Repair/Rearm/Refuel")
        self.hint = None
        self.threshold_seconds = 60*60*24*7

    def check_system(self, system):
        if not super(EDRStationRRRCheck, self).check_system(system):
            return False
        
        return system.get('distance', 1) >= 0 and system.get('distance', self.max_distance + 1) <= self.max_distance

    def check_station(self, station):
        if station.get("type", "") == "Fleet Carrier":
            return False

        if not super(EDRStationRRRCheck, self).check_station(station):
            return False

        if not (all(service in station['otherServices'] for service in ['Restock', 'Refuel', 'Repair'])):
            return False

        return True

    def is_service_availability_ambiguous(self, station):
        if not station.get('updateTime', None):
            return True

        if not station['updateTime'].get('information', None):
            return True
        
        updateTime=station['updateTime']['information']
        edt = EDTime()
        edt.from_edsm_timestamp(updateTime)
        return edt.older_than(self.threshold_seconds)

class EDRFleetCarrierRRRCheck(EDRSystemStationCheck):

    def __init__(self, max_distance, max_sc_distance):
        super(EDRFleetCarrierRRRCheck, self).__init__()
        self.max_distance = max_distance
        self.max_sc_distance = max_sc_distance
        self.name = _(u"Fleet Carrier with Repair/Rearm/Refuel")
        self.hint = None
        self.threshold_seconds = 60*60*24*2

    def check_system(self, system):
        if not super(EDRFleetCarrierRRRCheck, self).check_system(system):
            return False
        
        return system.get('distance', 1) >= 0 and system.get('distance', self.max_distance + 1) <= self.max_distance

    def check_station(self, station):
        if station.get("type", "") != "Fleet Carrier":
            return False

        if not super(EDRFleetCarrierRRRCheck, self).check_station(station):
            return False

        if not (all(service in station['otherServices'] for service in ['Restock', 'Refuel', 'Repair'])):
            return False

        return True

    def is_service_availability_ambiguous(self, station):
        if not station.get('updateTime', None):
            return True

        if not station['updateTime'].get('information', None):
            return True
        
        updateTime=station['updateTime']['information']
        edt = EDTime()
        edt.from_edsm_timestamp(updateTime)
        return edt.older_than(self.threshold_seconds)

class EDRMaterialTraderBasicCheck(EDRStationServiceCheck):

    def __init__(self):
        super(EDRMaterialTraderBasicCheck, self).__init__('Material Trader')

    def check_system(self, system):
        if not super(EDRMaterialTraderBasicCheck, self).check_system(system):
            return False

        if not system or not system.get('information', None):
            return False

        info = system['information']
        info['security'] = info.get('security', 'N/A')
        info['government'] = info.get('government', 'N/A')
        info['population'] = info.get('population', 0)
        
        if info['government'] == 'Anarchy' or info['security'].lower() not in ['high', 'medium']:
            return False
            
        if info['population'] < 1000000 or info['population'] > 22000000:
            return False
        
        if info['economy'].lower() not in ['extraction', 'refinery', 'industrial', 'high tech', 'military']:
            return False
        
        return True


class EDRRawTraderCheck(EDRMaterialTraderBasicCheck):
    def __init__(self):
        super(EDRRawTraderCheck, self).__init__()
        self.name = 'Raw material trader'
        self.hint = _(u"Found in systems with medium-high security, an 'extraction' or 'refinery' economy, a rather large population (>= 1 million)")

    def check_system(self, system):
        if system.get('name', '') in ['Kojeara']:
            return True

        if not super(EDRRawTraderCheck, self).check_system(system):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')
        
        return info['economy'].lower() in ['extraction', 'refinery']

    def check_station(self, station):
        if station.get('name', '') in ["TolaGarf's Junkyard"]:
            return True
        return super(EDRRawTraderCheck, self).check_station(station)

    def is_service_availability_ambiguous(self, station):
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['industrial', 'high tech', 'military']

class EDRManufacturedTraderCheck(EDRMaterialTraderBasicCheck):
    def __init__(self):
        super(EDRManufacturedTraderCheck, self).__init__()
        self.name = 'Manufactured material trader'
        self.hint = _(u"Found in systems with medium-high security, an 'industrial' economy, and a rather large population (>= 1 million)")

    def check_system(self, system):
        if system.get('name', '') in ['Coeus']:
            return True

        if not super(EDRManufacturedTraderCheck, self).check_system(system):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')
        
        return info['economy'].lower() == 'industrial'

    def check_station(self, station):
        if station.get('name', '') in ["Foster Terminal"]:
            return True
        return super(EDRManufacturedTraderCheck, self).check_station(station)

    def is_service_availability_ambiguous(self, station):
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['extraction', 'refinery', 'high tech', 'military']


class EDREncodedTraderCheck(EDRMaterialTraderBasicCheck):
    def __init__(self):
        super(EDREncodedTraderCheck, self).__init__()
        self.name = 'Encoded data trader'
        self.hint = _(u"Found in systems with medium-high security, a 'high tech' or 'military' economy, and a rather large population (>= 1 million)")

    def check_system(self, system):
        if system.get('name', '') in ['Ratraii']:
            return True

        if not super(EDREncodedTraderCheck, self).check_system(system):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')

        return info['economy'].lower() in ['high tech', 'military']

    def check_station(self, station):
        if station.get('name', '') in ["Colonia Dream"]:
            return True
        return super(EDREncodedTraderCheck, self).check_station(station)

    def is_service_availability_ambiguous(self, station):
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['extraction', 'refinery', 'industrial']


class EDRBlackMarketCheck(EDRStationServiceCheck):

    def __init__(self):
        super(EDRBlackMarketCheck, self).__init__('Black Market')

    def check_system(self, system):
        if not super(EDRBlackMarketCheck, self).check_system(system):
            return False

        if not system or not system.get('information', None):
            return False

        if not system.get('information', None):
            return False

        info = system['information']
        info['security'] = info.get('security', 'N/A')
        info['government'] = info.get('government', 'N/A')
        
        if info['government'] == 'Anarchy':
            return True
        
        if info['security'].lower() == 'low':
            return True
        
        return False

class EDRHumanTechBrokerCheck(EDRStationServiceCheck):
    def __init__(self):
        super(EDRHumanTechBrokerCheck, self).__init__('Technology Broker')
        self.name = _(u'Human Technology Broker')
        self.hint = _(u"Found in systems with an 'Industrial' economy', and a rather large population (>= 1 million)")

    def check_system(self, system):
        if system.get('name', '') in ['Tir']:
            return True

        if not super(EDRHumanTechBrokerCheck, self).check_system(system):
            return False

        if not system.get('information', None):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')
        info['population'] = info.get('population', 0)
        
        if info['population'] < 1000000:
            return False

        return info['economy'].lower() == 'industrial'

    def check_station(self, station):
        if station.get('name', '') in ["Bolden's Enterprise"]:
            return True
        return super(EDRHumanTechBrokerCheck, self).check_station(station)
    
    def is_service_availability_ambiguous(self, station):
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['high tech']
    
class EDRGuardianTechBrokerCheck(EDRStationServiceCheck):
    def __init__(self):
        super(EDRGuardianTechBrokerCheck, self).__init__('Technology Broker')
        self.name = _(u'Guardian Technology Broker')
        self.hint = _(u"Found in systems with a 'high tech' economy', and a rather large population (>= 1 million)")

    def check_system(self, system):
        if system.get('name', '') in ['Colonia']:
            return True

        if not super(EDRGuardianTechBrokerCheck, self).check_system(system):
            return False

        if not system.get('information', None):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')
        info['population'] = info.get('population', 0)
        
        if info['population'] < 1000000:
            return False

        return info['economy'].lower() == 'high tech'

    def check_station(self, station):
        if station.get('name', '') in ["Jaques Station"]:
            return True
        return super(EDRGuardianTechBrokerCheck, self).check_station(station)

    def is_service_availability_ambiguous(self, station):
        if not station or not station.get("secondEconomy", None):
            return False
        return station["secondEconomy"].lower() in ['industrial']

class EDROffBeatStationCheck(EDRApexSystemStationCheck):

    def __init__(self, max_distance_sc=100000):
        super(EDROffBeatStationCheck, self).__init__(max_distance_sc or 100000)
        self.name = _(u"Offbeat station")
        self.hint = _(u"Look for low traffic systems with stations that haven't been visited in a while.")
        self.threshold_seconds = 60*60*24*14
        
    def check_system(self, system):
        if not super(EDROffBeatStationCheck, self).check_system(system):
            return False
        
        return system.get('distance', 0) > 0 and system.get('distance', self.max_distance + 1) <= self.max_distance

    def check_station(self, station):
        if not super(EDROffBeatStationCheck, self).check_station(station):
            return False

        if not station.get('updateTime', None):
            return True

        if not station['updateTime'].get('information', None):
            return True
        
        updateTime=station['updateTime']['information']
        edt = EDTime()
        edt.from_edsm_timestamp(updateTime)
        return edt.older_than(self.threshold_seconds)

    def is_service_availability_ambiguous(self, station):
        if not station.get('updateTime', None):
            return False

        if not station['updateTime'].get('information', None):
            return False
        
        updateTime=station['updateTime']['information']
        edt = EDTime()
        edt.from_edsm_timestamp(updateTime)
        if not edt.older_than(self.threshold_seconds):
            return True
        close_call = not edt.older_than(self.threshold_seconds*1.25)
        return close_call