class EDRStationServiceCheck(object):

    def __init__(self, service):
        self.large_landing_pad = True
        self.service = service

    def check_system(self, system):
        return system != None

    def check_station(self, station):
        if not station:
            return False
        
        if not self.service:
            return True

        if not station.get('otherServices', None):
            return False
        
        return self.service in station['otherServices']

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

    def check_system(self, system):
        if not super(EDRRawTraderCheck, self).check_system(system):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')
        
        return info['economy'].lower() in ['extraction', 'refinery']


class EDRManufacturedTraderCheck(EDRMaterialTraderBasicCheck):
    def __init__(self):
        super(EDRManufacturedTraderCheck, self).__init__()

    def check_system(self, system):
        if not super(EDRManufacturedTraderCheck, self).check_system(system):
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')
        
        return info['economy'].lower() == 'industrial'


class EDREncodedTraderCheck(EDRMaterialTraderBasicCheck):
    def __init__(self):
        super(EDREncodedTraderCheck, self).__init__()

    def checks_out(self, system):
        if not super(EDREncodedTraderCheck, self).check_system():
            return False

        info = system['information']
        info['economy'] = info.get('economy', 'N/A')

        return info['economy'].lower() in ['high tech', 'military']


class EDRBlackMarketCheck(EDRStationServiceCheck):

    def __init__(self):
        super(EDRBlackMarketCheck, self).__init__('Black Market')

    def check_system(self, system):
        if not super(EDRBlackMarketCheck, self).check_system(system):
            return False

        if not system or not system.get('information', None):
            return False

        info = system['information']
        info['security'] = info.get('security', 'N/A')
        info['government'] = info.get('government', 'N/A')
        
        if info['government'] == 'Anarchy':
            return True
        
        if info['security'].lower() == 'low':
            return True
        
        return False