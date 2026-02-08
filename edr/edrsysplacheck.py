from edri18n import _, _c, _edr
from edrlog import EDR_LOG

class EDRSystemPlanetCheck:
    """
    Checks if a planet meets specific criteria (conditions, distance, etc.).
    """

    def __init__(self, edrsystems, sc_override=1500):
        """
        Initialize the check.

        Args:
            edrsystems: EDRSystems instance.
            sc_override: Max supercruise distance.
        """
        self.max_distance = 50
        self.max_sc_distance = sc_override
        self.name = None
        self.hint = None
        self.systems_counter = 0
        self.planets_counter = 0
        self.dlc_name = None
        self.edrsystems = edrsystems
        self.atmospheres = set()
        self.planet_classes = set()
        self.min_temperature = None
        self.max_temperature = None
        self.max_gravity = None
        self.parent_star_types = set()
        self.min_parent_star_distance = None
        self.volcanisms = set()
        
    def set_dlc(self, name):
        """
        Set DLC compatibility.
        """
        self.dlc_name = name

    def check_system(self, system):
        """
        Check if system is within max distance.
        """
        self.systems_counter = self.systems_counter + 1
        if not system:
            return False
        
        if system.get('distance', None) is None:
            return False
        
        return system['distance'] <= self.max_distance

    def check_planet(self, planet, system_name):
        """
        Check if planet meets all criteria.
        """
        self.planets_counter = self.planets_counter + 1
        if not planet:
            return False

        if planet.get('distanceToArrival', None) is None:
            return False

        if self.max_sc_distance and planet['distanceToArrival'] > self.max_sc_distance:
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if self.atmospheres and not atmosphere in self.atmospheres:
            return False
        
        planet_class = self.edrsystems.canonical_planet_class(planet)
        if self.planet_classes and not planet_class in self.planet_classes:
            return False
        
        mean_temperature = planet.get("surfaceTemperature", 1000)
        if self.min_temperature and mean_temperature < self.min_temperature:
            return False
        if self.max_temperature and mean_temperature > self.max_temperature:
            return False
        
        volcanism = planet.get("volcanism","")
        if self.volcanisms and volcanism not in self.volcanisms:
            return False

        if self.parent_star_types:
            star_type = self.edrsystems.parent_star_type(system_name, planet)
            if not star_type in self.parent_star_types:
                return False
            
        if self.min_parent_star_distance and self.edrsystems.parent_star_distance(system_name, planet) < self.min_parent_star_distance:
            return False
        
        if self.max_gravity and planet.get("gravity", 100) > self.max_gravity:
            return False
        
        return True

class EDRAmmoniaAtmosphereCheck(EDRSystemPlanetCheck):

    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Biology & water atmosphere')
        self.atmospheres = set(["ammonia"])

class EDRBiologyCheck(EDRSystemPlanetCheck):
    """
    Base class for biological checks.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Biology')
        self.genus = None

    def check_planet(self, planet, system_name):
        """
        Check if planet meets biological conditions.
        """
        if not super().check_planet(planet, system_name):
            EDR_LOG.debug("SystemPlanetCheck check planet failed: {}".format(planet))
            return False
        
        if not self.edrsystems.meets_biome_conditions(planet):
            EDR_LOG.debug("BiologyCheck meets_biome_conditions failed: {}".format(planet))
            return False
    
        genuses = planet.get("genuses", [])
        if genuses and self.genus:
            cgenus = self.genus.lower()
            for g in genuses:
                EDR_LOG.debug("Checking genus {} in {} ".format(cgenus, g))
                if cgenus in g["Genus"]:
                    EDR_LOG.debug("Found genus {} in {}".format(cgenus, planet))
                    return True
        else:
            EDR_LOG.debug("Found planet {}".format(planet))
            return True
        return False

class EDRWaterBiologyCheck(EDRBiologyCheck):
    """
    Checks for biology in water/water-rich atmospheres.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Biology & water atmosphere')
        self.atmospheres = set(["water", "waterrich"])

    
    
    
class EDRAleoidaCheck(EDRBiologyCheck):
    """
    Base check for Aleoida genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Aleoida')
        self.genus = "$codex_ent_aleoids_genus_name;"
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia", "carbondioxide", "carbondioxiderich"])

    def check_planet(self, planet, system_name):
        """
        Check specific conditions for Aleoida (temperature/atmosphere).
        """
        if not super().check_planet(planet, system_name):
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature >= 175 and mean_temperature <= 195
        
        return True
    
class EDRAleoidaArcusCheck(EDRAleoidaCheck):
    """
    Checks for Aleoida Arcus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Aleoida Arcus')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.min_temperature = 175
        self.max_temperature = 180

    
    
class EDRAleoidaCoronamusCheck(EDRAleoidaCheck):
    """
    Checks for Aleoida Coronamus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Aleoida Coronamus')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.min_temperature = 180
        self.max_temperature = 190

    
    
class EDRAleoidaGravisCheck(EDRAleoidaCheck):
    """
    Checks for Aleoida Gravis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Aleoida Gravis')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.min_temperature = 190
        self.max_temperature = 195

    
    
class EDRAleoidaLaminiaeCheck(EDRAleoidaCheck):
    """
    Checks for Aleoida Laminiae.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Aleoida Laminiae')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia"])

    
    
class EDRAleoidaSpicaCheck(EDRAleoidaCheck):
    """
    Checks for Aleoida Spica.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Aleoida Spica')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia"])


class EDRBacteriumCheck(EDRBiologyCheck):
    """
    Base check for Bacterium genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium')
        self.genus = "$codex_ent_bacterial_genus_name;"
    
class EDRBacteriumNebulusCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Nebulus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Nebulus')
        self.atmospheres = set(["helium"])

class EDRBacteriumAciesCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Acies.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Acies')
        self.atmospheres = set(["neon", "neonrich"])
    
class EDRBacteriumOmentumCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Omentum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Omentum')
        self.atmospheres = set(["neon", "neonrich"])
        self.volcanisms = set(["nitrogen", "ammonia"])

class EDRBacteriumScopulumCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Scopulum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Scopulum')
        self.atmospheres = set(["neon", "neonrich"])
        self.volcanisms = set(["carbon", "methane"])

class EDRBacteriumVerrataCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Verrata.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Verrata')
        self.atmospheres = set(["neon", "neonrich"])
        self.volcanisms = set(["water"])

class EDRBacteriumBullarisCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Bullaris.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Bullaris')
        self.atmospheres = set(["methane", "methanerich"])

class EDRBacteriumVesiculaCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Vesicula.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Vesicula')
        self.atmospheres = set(["argon", "argonrich"])

class EDRBacteriumInformemCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Informem.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Informem')
        self.atmospheres = set(["nitrogen"])

class EDRBacteriumVoluCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Volu.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Volu')
        self.atmospheres = set(["oxygen"])

class EDRBacteriumAlcyoneumCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Alcyoneum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Alcyoneum')
        self.atmospheres = set(["ammonia"])

class EDRBacteriumAurasusCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Aurasus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Aurasus')
        self.atmospheres = set(["carbon", "carbondioxide"])

class EDRBacteriumCerbrusCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Cerbrus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Cerbrus')
        self.atmospheres = set(["water", "waterrich", "sulphurdioxide"])

class EDRBacteriumTelaCheck(EDRBacteriumCheck):
    """
    Checks for Bacterium Tela.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Bacterium Tela')
        self.atmospheres = set() # any atmosphere
        self.volcanisms = set(["helium", "iron", "silicate"])
    
class EDRCactoidaCheck(EDRBiologyCheck):
    """
    Base check for Cactoida genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Cactoida')
        self.genus = "$codex_ent_cactoida_genus_name;"
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia", "carbondioxide", "carbondioxiderich", "water"])
    
    def check_planet(self, planet, system_name):
        """
        Check conditions for Cactoida.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature >= 180 and mean_temperature <= 195
        
        return True

class EDRCactoidaCortexumCheck(EDRCactoidaCheck):
    """
    Checks for Cactoida Cortexum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Cactoida Cortexum')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.min_temperature = 180
        self.max_temperature = 195

        

class EDRCactoidaPullulantaCheck(EDRCactoidaCheck):
    """
    Checks for Cactoida Pullulanta.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Cactoida Pullulanta')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.min_temperature = 180
        self.max_temperature = 195

    
    
class EDRCactoidaLapisCheck(EDRCactoidaCheck):
    """
    Checks for Cactoida Lapis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Cactoida Lapis')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia"])

          
    
class EDRCactoidaPeperatisCheck(EDRCactoidaCheck):
    """
    Checks for Cactoida Peperatis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Cactoida Peperatis')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia"])

          

class EDRCactoidaVermisCheck(EDRCactoidaCheck):
    """
    Checks for Cactoida Vermis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Cactoida Vermis')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["water"])

    

class EDRClypeusCheck(EDRBiologyCheck):
    """
    Base check for Clypeus genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Clypeus')
        self.genus = "$codex_ent_clypeus_genus_name;"
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "water"])
        self.min_temperature = 190

    
    
class EDRClypeusLacrimanCheck(EDRClypeusCheck):
    """
    Checks for Clypeus Lacriman.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Clypeus Lacriman')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "water"])
        self.min_temperature = 190

    

class EDRClypeusMargaritusCheck(EDRClypeusCheck):
    """
    Checks for Clypeus Margaritus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Clypeus Margaritus')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "water"])
        self.min_temperature = 190    
    
class EDRClypeusSpeculumiCheck(EDRClypeusCheck):
    """
    Checks for Clypeus Speculumi.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Clypeus Speculumi')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "water"])
        self.min_temperature = 190
        self.min_parent_star_distance = 2500


class EDRConchaCheck(EDRBiologyCheck):
    """
    Base check for Concha genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Concha')
        self.genus = "$codex_ent_conchas_genus_name;"
        self.atmospheres = set(["ammonia", "carbondioxide", "carbondioxiderich", "water", "waterrich", "nitrogen"])
    
class EDRConchaAureolasCheck(EDRConchaCheck):
    """
    Checks for Concha Aureolas.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Concha Aureolas')
        self.atmospheres = set(["ammonia"])

    
        
class EDRConchaBiconcavisCheck(EDRConchaCheck):
    """
    Checks for Concha Biconcavis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Concha Biconcavis')
        self.atmospheres = set(["nitrogen"])

    
    
class EDRConchaLabiataCheck(EDRConchaCheck):
    """
    Checks for Concha Labiata.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Concha Labiata')
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.max_temperature = 190

    

class EDRConchaRenibusCheck(EDRConchaCheck):
    """
    Checks for Concha Renibus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Concha Renibus')
        self.atmospheres = set(["carbondioxide", "carbondioxiderich", "water", "waterrich"])
    
    def check_planet(self, planet, system_name):
        """
        Check conditions for Concha Renibus.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature <= 195 and mean_temperature >= 180
        
        return True

class EDRElectricaeCheck(EDRBiologyCheck):
    """
    Base check for Electricae genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Electricae')
        self.genus = "$codex_ent_electricae_genus_name;"
        self.planet_classes = set(["icy"])
        self.atmospheres = set(["helium", "neon", "argon"])
    
    def check_planet(self, planet, system_name):
        """
        Check conditions for Electricae (Nebula or Star Type).
        """
        if not super().check_planet(planet, system_name):
            return False
        
        near_nebula = self.edrsystems.near_nebula(system_name)

        self.parent_star_types = set(["A", "Neutron", "White Dwarf (DA)", "DA"])
        star_type = self.edrsystems.parent_star_type(system_name, planet)
        if not star_type in self.parent_star_types:
            return near_nebula
        
        if star_type == "A":
            return self.edrsystems.parent_star_luminosity(system_name, planet).startswith("V")
        
        return near_nebula

class EDRElectricaePlumaCheck(EDRElectricaeCheck):
    """
    Checks for Electricae Pluma.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Electricae Pluma')
        self.genus = "$codex_ent_electricae_genus_name;"

class EDRElectricaeRadialemCheck(EDRElectricaeCheck):
    """
    Checks for Electricae Radialem.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Electricae Radialem')
        self.genus = "$codex_ent_electricae_genus_name;"
        self.parent_star_types = set()

    def check_planet(self, planet, system_name):
        """
        Check conditions for Electricae Radialem (Nebula).
        """
        if not super().check_planet(planet, system_name):
            return False
        
        return self.edrsystems.near_nebula(system_name)
    

class EDRFonticuluaCheck(EDRBiologyCheck):
    """
    Base check for Fonticulua genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fonticulua')
        self.genus = "$codex_ent_fonticulus_genus_name;"
        self.planet_classes = set(["icy", "rockyice"])

class EDRFonticuluaCampestrisCheck(EDRFonticuluaCheck):
    """
    Checks for Fonticulua Campestris.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fonticulua Campestris')
        self.planet_classes = set(["icy", "rockyice"])
        self.atmospheres = set(["argon"])

class EDRFonticuluaDigitosCheck(EDRFonticuluaCheck):
    """
    Checks for Fonticulua Digitos.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fonticulua Digitos')
        self.planet_classes = set(["icy", "rockyice"])
        self.atmospheres = set(["methane", "methanerich"])

class EDRFonticuluaFluctusCheck(EDRFonticuluaCheck):
    """
    Checks for Fonticulua Fluctus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fonticulua Fluctus')
        self.planet_classes = set(["icy", "rockyice"])
        self.atmospheres = set(["oxygen"])
    
class EDRFonticuluaLapidaCheck(EDRFonticuluaCheck):
    """
    Checks for Fonticulua Lapida.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fonticulua Lapida')
        self.planet_classes = set(["icy", "rockyice"])
        self.atmospheres = set(["nitrogen"])

class EDRFonticuluaSegmentatusCheck(EDRFonticuluaCheck):
    """
    Checks for Fonticulua Segmentatus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fonticulua Segmentatus')
        self.planet_classes = set(["icy", "rockyice"])
        self.atmospheres = set(["neon", "neonrich"])

class EDRFonticuluaUpupamCheck(EDRFonticuluaCheck):
    """
    Checks for Fonticulua Upupam.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fonticulua Upupam')
        self.planet_classes = set(["icy", "rockyice"])
        self.atmospheres = set(["argonrich"])

    
class EDRFrutexaCheck(EDRBiologyCheck):
    """
    Base check for Frutexa genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Frutexa')
        self.genus = "$codex_ent_shrubs_genus_name;"
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia", "carbondioxide", "carbondioxiderich", "water", "waterrich", "sulphurdioxide"])    
    
    def check_planet(self, planet, system_name):
        """
        Check conditions for Frutexa.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature <= 195
        elif atmosphere in ["water", "waterrich", "sulphurdioxide"]:
            return self.edrsystems.canonical_planet_class(planet) == "rocky"
                
        return True

class EDRFrutexaAcusCheck(EDRFrutexaCheck):
    """
    Checks for Frutexa Acus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Frutexa Acus')
        self.genus = "$codex_ent_shrubs_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.max_temperature = 195

class EDRFrutexaCollumCheck(EDRFrutexaCheck):
    """
    Checks for Frutexa Collum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Frutexa Collum')
        self.genus = "$codex_ent_shrubs_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["sulphurdioxide"])

class EDRFrutexaFeraCheck(EDRFrutexaCheck):
    """
    Checks for Frutexa Fera.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Frutexa Fera')
        self.genus = "$codex_ent_shrubs_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.max_temperature = 195

class EDRFrutexaFlabellumCheck(EDRFrutexaCheck):
    """
    Checks for Frutexa Flabellum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Frutexa Flabellum')
        self.genus = "$codex_ent_shrubs_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia"])

class EDRFrutexaFlammasisCheck(EDRFrutexaCheck):
    """
    Checks for Frutexa Flammasis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Frutexa Flammasis')
        self.genus = "$codex_ent_shrubs_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia"])

class EDRFrutexaMetallicumCheck(EDRFrutexaCheck):
    """
    Checks for Frutexa Metallicum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Frutexa Metallicum')
        self.genus = "$codex_ent_shrubs_genus_name;"
        self.planet_classes = set(["highmetalcontent"])
        self.atmospheres = set(["ammonia", "carbondioxide", "carbondioxiderich"])
    
    def check_planet(self, planet, system_name):
        """
        Check conditions for Frutexa Metallicum.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature <= 195
        
        return True

class EDRFrutexaSponsaeCheck(EDRFrutexaCheck):
    """
    Checks for Frutexa Sponsae.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Frutexa Sponsae')
        self.genus = "$codex_ent_shrubs_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["water", "waterrich"])

    
class EDRFungoidaCheck(EDRBiologyCheck):
    """
    Base check for Fungoida genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fungoida')
        self.genus = "$codex_ent_fungoids_genus_name;"
        self.atmospheres = set(["ammonia", "methane", "methanerich", "argon", "argonrich", "carbondioxide", "carbondioxiderich", "water", "waterrich"])

    def check_planet(self, planet, system_name):
        """
        Check conditions for Fungoida.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature >= 180 and mean_temperature <= 195
                
        return True
    
class EDRFungoidaBullarumCheck(EDRFungoidaCheck):
    """
    Checks for Fungoida Bullarum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fungoida Bullarum')
        self.atmospheres = set(["argon", "argonrich"])    

class EDRFungoidaGelataCheck(EDRFungoidaCheck):
    """
    Checks for Fungoida Gelata.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fungoida Gelata')
        self.atmospheres = set(["carbondioxide", "carbondioxiderich", "water", "waterrich"])
        self.min_temperature = 180
        self.max_temperature = 195

class EDRFungoidaSetisisCheck(EDRFungoidaCheck):
    """
    Checks for Fungoida Setisis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fungoida Setisis')
        self.atmospheres = set(["ammonia", "methane", "methanerich"])
    
class EDRFungoidaStabitisCheck(EDRFungoidaCheck):
    """
    Checks for Fungoida Stabitis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Fungoida Stabitis')
        self.atmospheres = set(["carbondioxide", "carbondioxiderich", "water", "waterrich"])
        self.min_temperature = 180
        self.max_temperature = 195
    

class EDROsseusCheck(EDRBiologyCheck):
    """
    Base check for Osseus genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Osseus')
        self.genus = "$codex_ent_osseus_genus_name;"
        self.planet_classes = set(["rocky", "highmetalcontent", "rockyice"])
        self.atmospheres = set(["ammonia", "methane", "methanerich", "argon", "argonrich", "carbondioxide", "carbondioxiderich", "water", "waterrich", "nitrogen"])

    def check_planet(self, planet, system_name):
        """
        Check conditions for Osseus.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature >= 180 and mean_temperature <= 195
                
        return True
    
class EDROsseusCornibusCheck(EDROsseusCheck):
    """
    Checks for Osseus Cornibus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Osseus Cornibus')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.min_temperature = 180
        self.max_temperature = 195

class EDROsseusDiscusCheck(EDROsseusCheck):
    """
    Checks for Osseus Discus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Osseus Discus')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["water", "waterrich"])

class EDROsseusFractusCheck(EDROsseusCheck):
    """
    Checks for Osseus Fractus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Osseus Fractus')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.min_temperature = 180
        self.max_temperature = 190
    
class EDROsseusPellebantusCheck(EDROsseusCheck):
    """
    Checks for Osseus Pellebantus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Osseus Pellebantus')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["carbondioxide", "carbondioxiderich"])
        self.min_temperature = 190
        self.max_temperature = 195
    
class EDROsseusPumiceCheck(EDROsseusCheck):
    """
    Checks for Osseus Pumice.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Osseus Pumice')
        self.planet_classes = set(["rockyice", "rocky", "highmetalcontent"])
        self.atmospheres = set(["methane", "methanerich", "argon", "argonrich", "nitrogen"])
        self.min_temperature = 180
        self.max_temperature = 190

class EDROsseusSpiralisCheck(EDROsseusCheck):
    """
    Checks for Osseus Spiralis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Osseus Spiralis')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia"])


class EDRReceptaCheck(EDRBiologyCheck):
    """
    Base check for Recepta genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Recepta')
        self.genus = "$codex_ent_recepta_genus_name;"
        self.planet_classes = set(["rocky", "highmetalcontent", "icy", "rockyice"])
        self.atmospheres = set(["sulphurdioxide"])

class EDRReceptaDeltahedronixCheck(EDRReceptaCheck):
    """
    Checks for Recepta Deltahedronix.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Recepta Deltahedronix')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["sulphurdioxide"])

class EDRReceptaUmbruxCheck(EDRReceptaCheck):
    """
    Checks for Recepta Umbrux.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Recepta Umbrux')
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["sulphurdioxide"])
    
class EDRReceptaConditivusCheck(EDRReceptaCheck):
    """
    Checks for Recepta Conditivus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Recepta Conditivus')
        self.planet_classes = set(["icy", "rockyice"])
        self.atmospheres = set(["sulphurdioxide"])

        
class EDRStratumCheck(EDRBiologyCheck):
    """
    Base check for Stratum genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 165
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["oxygen", "ammonia", "water", "waterrich", "carbondioxide", "carbondioxiderich", "sulphurdioxide"])

    def check_planet(self, planet, system_name):
        """
        Check conditions for Stratum.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        planet_class = self.edrsystems.canonical_planet_class(planet)
        atmosphere = self.edrsystems.canonical_atmosphere(planet)

        if planet_class == "rocky":
            return atmosphere in ["ammonia", "water", "waterrich", "carbondioxide", "carbondioxiderich", "sulphurdioxide"]
        elif planet_class == "highmetalcontent":
            return atmosphere in ["oxygen", "ammonia", "water", "waterrich", "carbondioxide", "carbondioxiderich", "sulphurdioxide"]
        return False

class EDRStratumAraneamusCheck(EDRBiologyCheck):
    """
    Checks for Stratum Araneamus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum Araneamus')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 165
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["sulphurdioxide"])

class EDRStratumCucumisisCheck(EDRBiologyCheck):
    """
    Checks for Stratum Cucumisis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum Cucumisis')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 190
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide", "sulphurdioxide"])

class EDRStratumExcutitusCheck(EDRBiologyCheck):
    """
    Checks for Stratum Excutitus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum Excutitus')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 165
        self.max_temperature = 190
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide", "sulphurdioxide"])

class EDRStratumFrigusCheck(EDRBiologyCheck):
    """
    Checks for Stratum Frigus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum Frigus')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 190
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide", "sulphurdioxide"])

class EDRStratumLaminamusCheck(EDRBiologyCheck):
    """
    Checks for Stratum Laminamus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum Laminamus')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 165
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia"])

class EDRStratumLimaxusCheck(EDRBiologyCheck):
    """
    Checks for Stratum Limaxus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum Limaxus')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 165
        self.max_temperature = 190
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["sulphurdioxide", "carbondioxide"])

class EDRStratumPaleasCheck(EDRBiologyCheck):
    """
    Checks for Stratum Paleas.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum Paleas')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 165
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia", "water", "carbondioxide"])

class EDRStratumTectonicasCheck(EDRBiologyCheck):
    """
    Checks for Stratum Tectonicas.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Stratum Tectonicas')
        self.genus = "$codex_ent_stratum_genus_name;"
        self.min_temperature = 165
        self.planet_classes = set(["highmetalcontent"])
        self.atmospheres = set(["oxygen", "ammonia", "water", "waterrich", "carbondioxide", "carbondioxiderich", "sulphurdioxide"])


class EDRTubusCheck(EDRBiologyCheck):
    """
    Base check for Tubus genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tubus')
        self.genus = "$codex_ent_tubus_genus_name;"
        self.planet_classes = set(["rocky", "highmetalcontent"])
        self.atmospheres = set(["ammonia", "carbondioxide", "carbondioxiderich"])

    def check_planet(self, planet, system_name):
        """
        Check conditions for Tubus.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        planet_class = self.edrsystems.canonical_planet_class(planet)
        if planet_class == "rocky":
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature >= 160 and mean_temperature <= 190
                
        return True
    
class EDRTubusCavasCheck(EDRBiologyCheck):
    """
    Checks for Tubus Cavas.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tubus Cavas')
        self.genus = "$codex_ent_tubus_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.min_temperature = 160
        self.max_temperature = 190
    
    def check_planet(self, planet, system_name):
        """
        Check conditions for Tubus Cavas.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        planet_class = self.edrsystems.canonical_planet_class(planet)
        if planet_class == "rocky":
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature >= 160 and mean_temperature <= 190
                
        return True
    
class EDRTubusCompagibusCheck(EDRBiologyCheck):
    """
    Checks for Tubus Compagibus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tubus Compagibus')
        self.genus = "$codex_ent_tubus_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.max_gravity = 0.15 * 9.81
        self.min_temperature = 160
        self.max_temperature = 190
    
class EDRTubusConiferCheck(EDRBiologyCheck):
    """
    Checks for Tubus Conifer.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tubus Conifer')
        self.genus = "$codex_ent_tubus_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.max_gravity = 0.15 * 9.81
        self.min_temperature = 160
        self.max_temperature = 190

class EDRTubusRosariumCheck(EDRBiologyCheck):
    """
    Checks for Tubus Rosarium.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tubus Rosarium')
        self.genus = "$codex_ent_tubus_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia"])
        self.max_gravity = 0.15 * 9.81
        self.min_temperature = 160
    
class EDRTubusSororibusCheck(EDRBiologyCheck):
    """
    Checks for Tubus Sororibus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tubus Sororibus')
        self.genus = "$codex_ent_tubus_genus_name;"
        self.planet_classes = set(["highmetalcontent"])
        self.atmospheres = set(["ammonia", "carbondioxide"])
        self.max_gravity = 0.15 * 9.81
        self.min_temperature = 160
        self.max_temperature = 190


class EDRTussockCheck(EDRBiologyCheck):
    """
    Base check for Tussock genus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia", "methane", "methanerich", "argon", "argonrich", "carbondioxide", "carbondioxiderich", "water", "waterrich", "sulphurdioxide"])
    
    def check_planet(self, planet, system_name):
        """
        Check conditions for Tussock.
        """
        if not super().check_planet(planet, system_name):
            return False
        
        atmosphere = self.edrsystems.canonical_atmosphere(planet)
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            mean_temperature = planet.get("surfaceTemperature", 1000)
            return mean_temperature >= 145 and mean_temperature <= 195
                
        return True

class EDRTussockAlbataCheck(EDRBiologyCheck):
    """
    Checks for Tussock Albata.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Albata')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.min_temperature = 175
        self.max_temperature = 180
        
class EDRTussockCapillumCheck(EDRBiologyCheck):
    """
    Checks for Tussock Capillum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Capillum')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["argon", "methane"])
        
class EDRTussockCaputusCheck(EDRBiologyCheck):
    """
    Checks for Tussock Caputus.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Caputus')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.min_temperature = 180
        self.max_temperature = 190
    
class EDRTussockCatenaCheck(EDRBiologyCheck):
    """
    Checks for Tussock Catena.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Catena')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia"])

class EDRTussockCultroCheck(EDRBiologyCheck):
    """
    Checks for Tussock Cultro.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Cultro')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia"])
        
class EDRTussockDivisaCheck(EDRBiologyCheck):
    """
    Checks for Tussock Divisa.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Divisa')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["ammonia"])
    
class EDRTussockIgnisCheck(EDRBiologyCheck):
    """
    Checks for Tussock Ignis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Ignis')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.min_temperature = 160
        self.max_temperature = 170
        
class EDRTussockPennataCheck(EDRBiologyCheck):
    """
    Checks for Tussock Pennata.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Pennata')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.min_temperature = 145
        self.max_temperature = 155
        
class EDRTussockPennatisCheck(EDRBiologyCheck):
    """
    Checks for Tussock Pennatis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Pennatis')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.max_temperature = 195
    
class EDRTussockPropagitoCheck(EDRBiologyCheck):
    """
    Checks for Tussock Propagito.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Propagito')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.max_temperature = 195
    
class EDRTussockSerratiCheck(EDRBiologyCheck):
    """
    Checks for Tussock Serrati.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Serrati')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.min_temperature = 170
        self.max_temperature = 175
        
class EDRTussockStigmasisCheck(EDRTussockCheck):
    """
    Checks for Tussock Stigmasis.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Stigmasis')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["sulphurdioxide"])

    
    
class EDRTussockTriticumCheck(EDRBiologyCheck):
    """
    Checks for Tussock Triticum.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Triticum')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.min_temperature = 190
        self.max_temperature = 195
    
class EDRTussockVentusaCheck(EDRBiologyCheck):
    """
    Checks for Tussock Ventusa.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Ventusa')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["carbondioxide"])
        self.min_temperature = 155
        self.max_temperature = 160
        
class EDRTussockVirgamCheck(EDRBiologyCheck):
    """
    Checks for Tussock Virgam.
    """
    def __init__(self, edrsystems, sc_override=1500):
        super().__init__(edrsystems, sc_override)
        self.name = _('Tussock Virgam')
        self.genus = "$codex_ent_tussocks_genus_name;"
        self.planet_classes = set(["rocky"])
        self.atmospheres = set(["water"])
        
class EDRGenusCheckerFactory:
    """
    Factory for creating biology checks based on genus/species names.
    """
    GENUS_LUT = {
        "aleoida": EDRAleoidaCheck,
        "aleoida arcus": EDRAleoidaArcusCheck,
        "aleoida coronamus": EDRAleoidaCoronamusCheck,
        "aleoida gravis": EDRAleoidaGravisCheck,
        "aleoida laminiae": EDRAleoidaLaminiaeCheck,
        "aleoida spica": EDRAleoidaSpicaCheck,

        "bacterium": EDRBacteriumCheck,
        "bacterium nebulus": EDRBacteriumNebulusCheck,
        "bacterium acies": EDRBacteriumAciesCheck,
        "bacterium omentum": EDRBacteriumOmentumCheck,
        "bacterium scopulum": EDRBacteriumScopulumCheck,
        "bacterium verrata": EDRBacteriumVerrataCheck,
        "bacterium bullaris": EDRBacteriumBullarisCheck,
        "bacterium vesicula": EDRBacteriumVesiculaCheck,
        "bacterium informem": EDRBacteriumInformemCheck,
        "bacterium volu": EDRBacteriumVoluCheck,
        "bacterium alcyoneum": EDRBacteriumAlcyoneumCheck,
        "bacterium aurasus": EDRBacteriumAurasusCheck,
        "bacterium cerbrus": EDRBacteriumCerbrusCheck,
        "bacterium tela": EDRBacteriumTelaCheck,

        "cactoida": EDRCactoidaCheck,
        "cactoida cortexum": EDRCactoidaCortexumCheck,
        "cactoida pullulanta": EDRCactoidaPullulantaCheck,
        "cactoida lapis": EDRCactoidaLapisCheck,
        "cactoida peperatis": EDRCactoidaPeperatisCheck,
        "cactoida vermis": EDRCactoidaVermisCheck,

        "clypeus": EDRClypeusCheck,
        "clypeus lacriman": EDRClypeusLacrimanCheck,
        "clypeus margaritus": EDRClypeusMargaritusCheck,
        "clypeus speculumi": EDRClypeusSpeculumiCheck,

        "concha": EDRConchaCheck,
        "concha aureolas": EDRConchaAureolasCheck,
        "concha biconcavis": EDRConchaBiconcavisCheck,
        "concha labiata": EDRConchaLabiataCheck,
        "concha renibus": EDRConchaRenibusCheck,

        "electricae": EDRElectricaeCheck,
        "electricae pluma": EDRElectricaePlumaCheck,
        "electricae radialem": EDRElectricaeRadialemCheck,

        "fonticulua": EDRFonticuluaCheck,
        "fonticulua campestris": EDRFonticuluaCampestrisCheck,
        "fonticulua digitos": EDRFonticuluaDigitosCheck,
        "fonticulua fluctus": EDRFonticuluaFluctusCheck,
        "fonticulua lapida": EDRFonticuluaLapidaCheck,
        "fonticulua segmentatus": EDRFonticuluaSegmentatusCheck,
        "fonticulua upupam": EDRFonticuluaUpupamCheck,

        "frutexa": EDRFrutexaCheck,
        "frutexa acus": EDRFrutexaAcusCheck,
        "frutexa collum": EDRFrutexaCollumCheck,
        "frutexa fera": EDRFrutexaFeraCheck,
        "frutexa flabellum": EDRFrutexaFlabellumCheck,
        "frutexa flammasis": EDRFrutexaFlammasisCheck,
        "frutexa metallica": EDRFrutexaMetallicumCheck,
        "frutexa sponsae": EDRFrutexaSponsaeCheck,

        "fungoida": EDRFungoidaCheck,
        "fungoida bullarum": EDRFungoidaBullarumCheck,
        "fungoida gelata": EDRFungoidaGelataCheck,
        "fungoida setisis": EDRFungoidaSetisisCheck,
        "fungoida stabitis": EDRFungoidaStabitisCheck,

        "osseus": EDROsseusCheck,
        "osseus cornibus": EDROsseusCornibusCheck,
        "osseus discus": EDROsseusDiscusCheck,
        "osseus fractus": EDROsseusFractusCheck,
        "osseus pellebantus": EDROsseusPellebantusCheck,
        "osseus pumice": EDROsseusPumiceCheck,
        "osseus spiralis": EDROsseusSpiralisCheck,

        "recepta": EDRReceptaCheck,
        "recepta deltahedronix": EDRReceptaDeltahedronixCheck,
        "recepta umbrux": EDRReceptaUmbruxCheck,
        "recepta conditivus": EDRReceptaConditivusCheck,

        "stratum": EDRStratumCheck,
        "stratum araneamus": EDRStratumAraneamusCheck,
        "stratum cucumisis": EDRStratumCucumisisCheck,
        "stratum excutitus": EDRStratumExcutitusCheck,
        "stratum frigus": EDRStratumFrigusCheck,
        "stratum laminamus": EDRStratumLaminamusCheck,
        "stratum limaxus": EDRStratumLimaxusCheck,
        "stratum paleas": EDRStratumPaleasCheck,
        "stratum tectonicas": EDRStratumTectonicasCheck,
        
        "tubus": EDRTubusCheck,
        "tubus cavas": EDRTubusCavasCheck,
        "tubus compagibus": EDRTubusCompagibusCheck,
        "tubus conifer": EDRTubusConiferCheck,
        "tubus rosarium": EDRTubusRosariumCheck,
        "tubus sororibus": EDRTubusSororibusCheck,

        "tussock": EDRTussockCheck,
        "tussock albata": EDRTussockAlbataCheck,
        "tussock capillum": EDRTussockCapillumCheck,
        "tussock caputus": EDRTussockCaputusCheck,
        "tussock catena": EDRTussockCatenaCheck,
        "tussock cultro": EDRTussockCultroCheck,
        "tussock divisa": EDRTussockDivisaCheck,
        "tussock ignis": EDRTussockIgnisCheck,
        "tussock pennata": EDRTussockPennataCheck,
        "tussock pennatis": EDRTussockPennatisCheck,
        "tussock propagito": EDRTussockPropagitoCheck,
        "tussock serrati": EDRTussockSerratiCheck,
        "tussock stigmasis": EDRTussockStigmasisCheck,
        "tussock triticum": EDRTussockTriticumCheck,
        "tussock ventusa": EDRTussockVentusaCheck,
        "tussock virgam": EDRTussockVirgamCheck,
        
        "biology": EDRBiologyCheck,
        "bio": EDRBiologyCheck,
        "water": EDRWaterBiologyCheck,
        "ammonia": EDRAmmoniaAtmosphereCheck,
    }

    @staticmethod
    def recognized_genus(genus):
        """
        Check if genus is recognized.
        """
        cgenus = genus.lower()
        return cgenus in EDRGenusCheckerFactory.GENUS_LUT

    @staticmethod
    def recognized_candidates(genus):
        """
        Get recognized candidates for genus search.
        """
        cgenus = genus.lower()
        keys = EDRGenusCheckerFactory.GENUS_LUT.keys()
        matches = [k for k in keys if cgenus in k or k.startswith(cgenus)]
        return matches


    @staticmethod
    def get_checker(genus, edrsystems, override_sc):
        """
        Get a checker instance for the given genus.
        """
        cgenus = genus.lower()
        return EDRGenusCheckerFactory.GENUS_LUT.get(cgenus, EDRBiologyCheck)(edrsystems, override_sc)