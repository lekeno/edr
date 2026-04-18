import pickle
from edr.core.edrlog import EDR_LOG

class EDRUnpickler(pickle.Unpickler):
    """
    Custom Unpickler to handle module renames and moves across EDR versions.
    Maps legacy top-level modules to their new locations within the edr package.
    """
    MODULE_MAPPING = {
        'lrucache': 'edr.utils.lrucache',
        'edrroutes': 'edr.controllers.edrroutes',
        'edrfleetcarrier': 'edr.models.edrfleetcarrier',
        'edentities': 'edr.models.edentities',
        'edrinventory': 'edr.models.edrinventory',
        'edropponents': 'edr.controllers.edropponents',
        'edtime': 'edr.utils.edtime',
        'edrconfig': 'edr.core.edrconfig',
        'edrlog': 'edr.core.edrlog',
        'edri18n': 'edr.core.edri18n',
        'edrutils': 'edr.utils.edrutils',
        'edrfleet': 'edr.models.edrfleet',
        'edvehicles': 'edr.models.edvehicles',
        'edrserver': 'edr.controllers.edrserver',
        'edsmserver': 'edr.controllers.edsmserver',
        'randomtips': 'edr.utils.randomtips',
        'audiofeedback': 'edr.utils.audiofeedback',
        'ingamemsg': 'edr.ui.ingamemsg',
        'edrclient': 'edr.controllers.edrclient',
        'edrfactions': 'edr.controllers.edrfactions',
        'edrcmdrprofile': 'edr.models.edrcmdrprofile',
        'edrcmdrs': 'edr.models.edrcmdrs',
        'edrlegalrecords': 'edr.models.edrlegalrecords',
        'edrsystems': 'edr.controllers.edrsystems',
        'edrresourcefinder': 'edr.controllers.edrresourcefinder',
        'edrhotkeys': 'edr.controllers.edrhotkeys',
        'edrminingstats': 'edr.controllers.edrminingstats',
        'edrbountyhuntingstats': 'edr.controllers.edrbountyhuntingstats',
        'edrdiscord': 'edr.controllers.edrdiscord',
        'edrfssinsights': 'edr.controllers.edrfssinsights',
        'edrbodiesofinterest': 'edr.models.edrbodiesofinterest',
        'edrscout': 'edr.controllers.edrscout',
        'edrbiology': 'edr.controllers.edrbiology',
        'edrrealtime': 'edr.controllers.edrrealtime',
        'edrservicecheck': 'edr.controllers.edrservicecheck',
        'edrsysplacheck': 'edr.controllers.edrsysplacheck',
        'edrsyssetlcheck': 'edr.controllers.edrsyssetlcheck',
        'edrsysstacheck': 'edr.controllers.edrsysstacheck',
        'edrparkingsystemfinder': 'edr.controllers.edrparkingsystemfinder',
        'edrplanetfinder': 'edr.controllers.edrplanetfinder',
        'edrsettlementfinder': 'edr.controllers.edrsettlementfinder',
        'edrservicefinder': 'edr.controllers.edrservicefinder',
        'edreventhandler': 'edr.controllers.edreventhandler',
        'edrcommands': 'edr.controllers.edrcommands',
        'edpilot': 'edr.models.edpilot',
        'edplayer': 'edr.models.edplayer',
        'edplayerone': 'edr.models.edplayerone',
        'edwing': 'edr.models.edwing',
        'edrcrew': 'edr.models.edrcrew',
        'edrsquadron': 'edr.models.edrsquadron',
        'edrpowerplay': 'edr.models.edrpowerplay',
        'edshipyard': 'edr.models.edshipyard',
        'edmodule': 'edr.models.edmodule',
        'edsitu': 'edr.models.edsitu',
        'edengineers': 'edr.models.edengineers',
        'edshield': 'edr.models.edshield',
        'edarmour': 'edr.models.edarmour',
        'edweapons': 'edr.models.edweapons',
        'edspacesuits': 'edr.models.edspacesuits',
        'edrrawdepletables': 'edr.models.edrrawdepletables',
        'RESTFirebase': 'edr.utils.RESTFirebase',
        'edrautoupdater': 'edr.core.edrautoupdater',
        'edropsec': 'edr.core.edropsec',
        'helpcontent': 'edr.core.helpcontent',
        'igmconfig': 'edr.core.igmconfig',
    }
    ENTITY_MAPPING = {
        'EDRCrew': 'edr.models.edrcrew',
        'EDRSquadronMember': 'edr.models.edrsquadron',
        'EDRPowerplay': 'edr.models.edrpowerplay',
        'EDRPowerplayUnknown': 'edr.models.edrpowerplay',
        'EDFineOrBounty': 'edr.models.edpilot',
        'EDPilot': 'edr.models.edpilot',
        'EDPlayer': 'edr.models.edplayer',
        'EDWing': 'edr.models.edwing',
        'EDPlayerOne': 'edr.models.edplayerone',
    }
    VEHICLE_MAPPING = {
        'EDSidewinder': 'edr.models.edshipyard', 'EDHauler': 'edr.models.edshipyard', 'EDEagle': 'edr.models.edshipyard', 'EDAdder': 'edr.models.edshipyard', 
        'EDAdderApex': 'edr.models.edshipyard', 'EDViperMkIII': 'edr.models.edshipyard', 'EDCobraMkIII': 'edr.models.edshipyard', 'EDT6Transporter': 'edr.models.edshipyard', 
        'EDDolphin': 'edr.models.edshipyard', 'EDT7Transporter': 'edr.models.edshipyard', 'EDT8Transporter': 'edr.models.edshipyard', 'EDAspExplorer': 'edr.models.edshipyard', 
        'EDCaspianExplorer': 'edr.models.edshipyard', 'EDVulture': 'edr.models.edshipyard', 'EDVultureFrontlines': 'edr.models.edshipyard', 'EDImperialClipper': 'edr.models.edshipyard', 
        'EDFederalDropship': 'edr.models.edshipyard', 'EDOrca': 'edr.models.edshipyard', 'EDT9Heavy': 'edr.models.edshipyard', 'EDT10Defender': 'edr.models.edshipyard', 
        'EDT11Prospector': 'edr.models.edshipyard', 'EDPantherClipperMkII': 'edr.models.edshipyard', 'EDPython': 'edr.models.edshipyard', 'EDPythonMkII': 'edr.models.edshipyard', 
        'EDBelugaLiner': 'edr.models.edshipyard', 'EDFerDeLance': 'edr.models.edshipyard', 'EDAnaconda': 'edr.models.edshipyard', 'EDFederalCorvette': 'edr.models.edshipyard', 
        'EDImperialCutter': 'edr.models.edshipyard', 'EDDiamondbackScout': 'edr.models.edshipyard', 'EDImperialCourier': 'edr.models.edshipyard', 'EDDiamondbackExplorer': 'edr.models.edshipyard', 
        'EDImperialEagle': 'edr.models.edshipyard', 'EDFederalAssaultShip': 'edr.models.edshipyard', 'EDFederalGunship': 'edr.models.edshipyard', 'EDViperMkIV': 'edr.models.edshipyard', 
        'EDCobraMkIV': 'edr.models.edshipyard', 'EDCobraMkV': 'edr.models.edshipyard', 'EDCorsair': 'edr.models.edshipyard', 'EDKeelback': 'edr.models.edshipyard', 
        'EDAspScout': 'edr.models.edshipyard', 'EDAllianceChieftain': 'edr.models.edshipyard', 'EDAllianceChallenger': 'edr.models.edshipyard', 'EDAllianceCrusader': 'edr.models.edshipyard', 
        'EDKraitMkII': 'edr.models.edshipyard', 'EDKraitPhantom': 'edr.models.edshipyard', 'EDMamba': 'edr.models.edshipyard', 'EDMandalay': 'edr.models.edshipyard', 
        'EDKestrelMkII': 'edr.models.edshipyard', 'EDImperialFighter': 'edr.models.edshipyard', 'EDF63Condor': 'edr.models.edshipyard', 'EDTaipanFighter': 'edr.models.edshipyard', 
        'EDTrident': 'edr.models.edshipyard', 'EDJavelin': 'edr.models.edshipyard', 'EDLance': 'edr.models.edshipyard', 'EDSRVScorpion': 'edr.models.edshipyard', 
        'EDSRVScarab': 'edr.models.edshipyard', 'EDVehicleFactory': 'edr.models.edshipyard',
        'EDTaxi': 'edr.models.edtaxi', 'EDShipLaunchedFighter': 'edr.models.edslf', 'EDSurfaceVehicle': 'edr.models.edsrv',
        'EDUnknownVehicle': 'edr.models.edunknownvehicle', 'EDCrewUnknownVehicle': 'edr.models.edunknownvehicle', 'EDCaptainUnknownVehicle': 'edr.models.edunknownvehicle'
    }

    def find_class(self, module, name):
        """
        Overrides the default find_class to apply module mapping.
        
        Args:
            module (str): The module name as recorded in the pickle file.
            name (str): The class name.
            
        Returns:
            type: The resolved class.
        """
        if module in self.MODULE_MAPPING:
            new_module = self.MODULE_MAPPING[module]
            EDR_LOG.debug(f"Remapping legacy pickle module '{module}' to '{new_module}' for class '{name}'")
            module = new_module
        
        # Handle classes that were previously in edentities but are now modularized
        if module == 'edr.models.edentities' and name in self.ENTITY_MAPPING:
            new_module = self.ENTITY_MAPPING[name]
            EDR_LOG.debug(f"Remapping class '{name}' from legacy module 'edentities' to '{new_module}'")
            module = new_module

        # Handle specific ship models moved out of edvehicles.py
        if module == 'edr.models.edvehicles' and name in self.VEHICLE_MAPPING:
            new_module = self.VEHICLE_MAPPING[name]
            EDR_LOG.debug(f"Remapping vehicle class '{name}' from legacy module 'edvehicles' to '{new_module}'")
            module = new_module

        # Also handle potential 'src.edr...' style paths if they were ever used
        if module.startswith('src.edr'):
            new_module = module[4:] # strip 'src.'
            EDR_LOG.debug(f"Stripping 'src.' prefix from module '{module}' -> '{new_module}'")
            module = new_module

        return super().find_class(module, name)

def edr_load_pickle(handle):
    """
    Universal helper to load a pickle file using EDRUnpickler for backward compatibility.
    
    Args:
        handle (file): An open file handle in binary read mode ('rb').
        
    Returns:
        object: The unpickled object instance.
    """
    return EDRUnpickler(handle).load()
