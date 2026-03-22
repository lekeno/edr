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
