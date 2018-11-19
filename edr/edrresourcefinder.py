# coding= utf-8
import edrsystems
import edrstatecheck
import edrstatefinder
from edri18n import _
import math

class EDRResourceFinder(object):

    SUPPORTED_RESOURCES = {
        "antimony": "ant", "tellurium": "tel", "ruthenium": "rut", "tungsten": "tun", "zirconium": "zir", "arsenic": "ars",
        "adaptive encryptors capture": "a e c", "atypical encryption archives": "a e a",
        "abnormal compact emission data": "a c e d", "datamined wake exceptions": "d w e",
        "decoded emission data": "d e d", "peculiar shield frequency data": "p s f d",
        "divergent scan data": "d s d", "classified scan databanks": "c s d",
        "security firmware patch": "s f p",
        "unexpected emission data": "u e d", "untypical shield scans": "u s s", "aberrant shield pattern analysis": "a s p a",
        "modified consumer firmware": "m c f", "modified embedded firmware": "m e f",
        "cracked industrial firmware": "c i f",  "specialized legacy firmware": "s l f",
        "open symmetric keys": "o s k",
        "classified scan fragment": "c s f", "unusual encrypted files": "uef", "tagged encryption codes": "t e c",
        "eccentric hyperspace trajectories": "e h t", "strange wake solutions": "s w s",
        "biotech conductors": "b c", "exquisite focus crystals": "e f c",
        "core dynamics composites": "c d c", "imperial shielding": "i s", "improvised components": "i c", "military grade alloys": "m g a",
        "military supercapacitors": "m s", "pharmaceutical isolators": "p i", "proto light alloys": "p l a",
        "proto radiolic alloys": "p r a", "proto heat radiators": "p h r", "proprietary composites": "pr c",
        "chemical manipulators": "c m", "compound shielding": "c s", "conductive polymers": "c p", "configurable components": "c co", "heat vanes": "h v",
        "polymer capacitors": "po c", "refined focus crystals": "r f c", "thermic alloys": "t a",
        "chemical distillery": "c d", "conductive ceramics": "c ce",
        "high density composites": "h d c", "mechanical components": "m c",
        "polonium": "pol", "technetium": "tec", "yttrium": "ytt", "cadmium": "cad", "mercury": "mer", "selenium": "sel", "tin": "tin",
        "molybdenum": "mol", "niobium": "nio",
        "chromium": "chr", "vanadium": "van", "zinc": "zin", "germaniun": "ger", "manganese": "man",
        "boron": "bor",
        "electrochemical arrays": "e a", "focus crystals": "f c",
        "heat exchangers": "h e", "shielding sensors": "s s",
        "phase alloys": "p a",
    }

    RESOURCE_SYNONYMS = {
        "ant": "antimony",  "tel": "tellurium", "rut": "ruthenium", "tun": "tungsten", "zir": "zirconium",
        "a e c" : "adaptive encryptors capture", "aec" : "adaptive encryptors capture", "adaptive encryptor capture" : "adaptive encryptors capture",
        "a e a": "atypical encryption archives", "aea": "atypical encryption archives", "atypical encryption archive": "atypical encryption archives",
        "a c e d": "abnormal compact emission data", "aced": "abnormal compact emission data",
        "d w e": "datamined wake exceptions", "datamined wake exception": "datamined wake exceptions", "datamined": "datamined wake exceptions",
        "d e d": "decoded emission data", "ded": "decoded emission data",
        "d s d": "divergent scan data", "dsd": "divergent scan data",
        "c s d": "classified scan databanks", "csd": "classified scan databanks", "classified scan databank": "classified scan databanks",
        "s f p": "security firmware patch", "sfp": "security firmware patch",
        "s w s": "strange wake solutions", "sws": "strange wake solutions", "strange wake solution": "strange wake solutions",
        "p s f d": "peculiar shield frequency data", "psfd": "peculiar shield frequency data", "peculiar": "peculiar shield frequency data",
        "u e d": "unexpected emission data", "ued": "unexpected emission data", "unexpected": "unexpected emission data", 
        "u s s": "untypical shield scans", "uss": "untypical shield scans", "untypical": "untypical shield scans",
        "a s p a": "aberrant shield pattern analysis", "aspa": "aberrant shield pattern analysis", "aberrant": "aberrant shield pattern analysis",
        "m c f": "modified consumer firmware", "mcf": "modified consumer firmware", "consumer firmware": "modified consumer firmware",
        "m e f": "modified embedded firmware", "mef": "modified embedded firmware", "embedded firmware": "modified embedded firmware",
        "c i f": "cracked industrial firmware", "cif": "cracked industrial firmware", "cracked firmware": "cracked industrial firmware",
        "s l f": "specialized legacy firmware", "slf": "specialized legacy firmware", "specialized firmware": "specialized legacy firmware",
        "c s f": "classified scan fragment", "csf": "classified scan fragment", "classified scan": "classified scan fragment", 
        "o s k": "open symmetric keys", "osk": "open symmetric keys", "open symmetric key": "open symmetric keys", "symmetric keys": "open symmetric keys",
        "u e f": "unusual encrypted files", "uef": "unusual encrypted files",
        "t e c": "tagged encryption codes",
        "e h t": "eccentric hyperspace trajectories", "eht": "eccentric hyperspace trajectories", "eccentric": "eccentric hyperspace trajectories", "eccentric hyperspace trajectory": "eccentric hyperspace trajectories",
        "b c": "biotech conductors", "bc": "biotech conductors", "biotech conductor": "biotech conductors",
        "e f c": "exquisite focus crystals", "efc": "exquisite focus crystals", "exq": "exquisite focus crystals", "exquisite focus crystal": "exquisite focus crystals",
        "c d c": "core dynamics composites", "core dyn": "core dynamics composites", "core": "core dynamics composites", "core dynamics composite": "core dynamics composites",
        "i s": "imperial shielding", "imperial shield": "imperial shielding", "imperial shields": "imperial shielding", "imperial": "imperial shielding", 
        "i c": "improvised components", "improvised": "improvised components", "improvised component": "improvised components",
        "m g a": "military grade alloys", "military alloys": "military grade alloys", "military alloy": "military grade alloys", "military grade": "military grade alloys",
        "m s": "military supercapacitors", "military supercapacitor": "military supercapacitors", "supercapacitor": "military supercapacitors", "supercapacitors": "military supercapacitors", "supercapa": "military supercapacitors",   
        "p i": "pharmaceutical isolators", "pharmaceutical isolator": "pharmaceutical isolators", "pharma": "pharmaceutical isolators", "isolators": "pharmaceutical isolators", "isolator": "pharmaceutical isolators",
        "p l a": "proto light alloys", "proto light alloy": "proto light alloys", "proto light": "proto light alloys", 
        "p r a": "proto radiolic alloys", "proto radiolic alloy": "proto radiolic alloys", "proto radiolic": "proto radiolic alloys", "radiolic": "proto radiolic alloys",
        "p h r": "proto heat radiators", "proto heat radiator": "proto heat radiators", "proto heat": "proto heat radiators", "proto radiator": "proto heat radiators",
        "p c": "ambiguous abbreviation (pc)",
        "c c": "ambiguous abbreviation (cc)",
        "c d": "chemical distillery",
        "pr c": "proprietary composites", "proprietary composite": "proprietary composites",
        "c m": "chemical manipulators", "c s": "compound shielding", "c p": "conductive polymers", "c co": "configurable components", "h v": "heat vanes",
        "po c": "polymer capacitors", "r f c": "refined focus crystals", "t a": "thermic alloys",
        "h d c": "high density composites", "m c": "mechanical components",
        "c ce": "conductive ceramics",
        "pol": "polonium", "polo": "polonium", "tec": "technetium", "ytt": "yttrium", "cad": "cadmium",
        "mer": "mercury", "sel": "selenium", "ars": "arsenic", "mol": "molybdenum",
        "nio": "niobium", "chr": "chromium", "van": "vanadium", "zin": "zinc", "ger": "germaniun", "man": "manganese",
        "bor": "boron",
        "e a": "electrochemical arrays", "electrochemical array": "electrochemical arrays",
        "f c": "focus crystals", "focus crystal": "focus crystals",
        "h e": "heat exchangers", "heat exchanger": "heat exchangers",
        "s s": "shielding sensors", "shielding sensor": "shielding sensors",
        "p a": "phase alloys", "phase alloy": "phase alloys",
    }

    RESOURCE_CALLBACKS = {
        "biotech conductors": 'mission_reward_only',
        "exquisite focus crystals": 'mission_reward_only',
        "antimony": 'recommend_crashed_site',
        "tellurium": 'recommend_crashed_site', "ruthenium": 'recommend_crashed_site', "tungsten": 'recommend_crashed_site',
        "zirconium": 'recommend_crashed_site', "adaptive encryptors capture": 'recommend_crashed_site',
        "atypical encryption archives": 'recommend_crashed_site', "modified consumer firmware": 'recommend_crashed_site',
        "modified embedded firmware": 'from_hacking',
        "divergent scan data": 'from_hacking',
        "security firmware patch": 'from_hacking',
        "open symmetric keys": 'from_hacking',
        "classified scan databanks": 'from_hacking',
        "abnormal compact emission data": 'from_combat_authority_scans_encoded_emissions',
        "datamined wake exceptions": 'state_dependent_resource',
        "decoded emission data": 'from_combat_authority_scans_encoded_emissions',
        "peculiar shield frequency data": 'from_isinor',
        "unexpected emission data": 'from_isinor',
        "untypical shield scans": 'from_isinor', 
        "aberrant shield pattern analysis": 'from_isinor',
        "cracked industrial firmware": 'recommend_crashed_site', "classified scan fragment": 'recommend_crashed_site',
        "unusual encrypted files": 'recommend_crashed_site', "tagged encryption codes": 'recommend_crashed_site',
        "specialized legacy firmware": 'recommend_crashed_site',
        "eccentric hyperspace trajectories": 'from_high_energy_wakes',
        "strange wake solutions": 'from_high_energy_wakes',
        "core dynamics composites": 'state_dependent_resource', "imperial shielding": 'state_dependent_resource', "improvised components": 'state_dependent_resource',
        "military grade alloys": 'state_dependent_resource', "military supercapacitors": 'state_dependent_resource',
        "pharmaceutical isolators": 'state_dependent_resource', "proto light alloys": 'state_dependent_resource',
        "proto radiolic alloys": 'state_dependent_resource', "proto heat radiators": 'state_dependent_resource', "proprietary composites": 'state_dependent_resource',
        "chemical manipulators": 'from_surface_site', "compound shielding": 'from_surface_site', "conductive polymers": 'from_surface_site', "configurable components": 'from_dav_hope', "heat vanes": 'from_surface_site',
        "polymer capacitors": 'from_surface_site', "refined focus crystals": 'from_surface_site', "thermic alloys": "state_dependent_resource",
        "high density composites": "from_dav_hope", "mechanical components": "from_dav_hope",
        "conductive ceramics": "from_surface_site", "chemical distillery": "from_surface_site",
        "electrochemical arrays": "from_surface_site", "focus crystals": "from_surface_site", "heat exchangers": "from_surface_site", "shielding sensors": "from_surface_site", "phase alloys": "from_surface_site",
        "polonium": 'recommend_prospecting_planet', "technetium": 'recommend_prospecting_planet', "yttrium": 'recommend_prospecting_planet', "cadmium": 'recommend_prospecting_planet', "mercury": 'recommend_prospecting_planet', "selenium": 'recommend_prospecting_planet', "tin": 'recommend_prospecting_planet',
        "arsenic": 'recommend_prospecting_planet', "molybdenum": 'recommend_prospecting_planet',
        "niobium": 'recommend_prospecting_planet', "chromium": 'recommend_prospecting_planet',
        "vanadium": 'recommend_prospecting_planet', "zinc": 'recommend_prospecting_planet',
        "germaniun": 'recommend_prospecting_planet', "man": 'recommend_prospecting_planet',
        "boron": 'mat_trader_mining_all',
        "ambiguous abbreviation (pc)": "ambiguous_p_c",
        "ambiguous abbreviation (cc)": "ambiguous_c_c",
    }

    def __init__(self, edr_systems, permits = []):
        self.edr_systems = edr_systems
        self.radius = 50
        self.permits = permits

    def canonical_name(self, resource):
        if not resource:
            return None

        cresource = resource.lower()
        if cresource not in self.SUPPORTED_RESOURCES:
            cresource = self.RESOURCE_SYNONYMS.get(cresource, None)
        return cresource

    def resource_near(self, resource, reference_system, callback):
        if not resource:
            return False

        cresource = self.canonical_name(resource)
        if cresource is None:
            return False

        if cresource not in self.RESOURCE_CALLBACKS:
            return False
        return getattr(self, self.RESOURCE_CALLBACKS[cresource])(cresource, reference_system, callback)

    def mission_reward_only(self, resource, reference_system, callback):
        return [
            _(u"Mission reward only."),
            _(u"Higher chance when allied to the factions giving missions."),
            _(u"Stacking passenger missions seems quite efficient."),
        ]

    def ambiguous_p_c(self, resource, reference_system, callback):
        return [
            _(u" - '!search pr c' for proprietary composites"),
            _(u" - '!search po c' for polymer capacitors"),
        ]

    def ambiguous_c_c(self, resource, reference_system, callback):
        return [
            _(u" - '!search c ce' for conductive ceramics"),
            _(u" - '!search c co' for configurable components"),
        ]
    
    def recommend_crashed_site(self, resource, reference_system, callback):
        if resource is None:
            return False

        if resource.lower() not in ["antimony", "tellurium", "ruthenium", "tungsten", "zirconium", "adaptive encryptors capture", "atypical encryption archives", "modified consumer firmware", "cracked industrial firmware", "classified scan fragment", "unusual encrypted files", "tagged encryption codes", "specialized legacy firmware"]:
            return False

        if resource.lower() in ["adaptive encryptors capture", "atypical encryption archives"]:
            to_bugkiller = self.edr_systems.distance(reference_system, "HIP 16613")
            to_jameson = self.edr_systems.distance(reference_system, "HIP 12099")
            if to_bugkiller <= to_jameson:
                pretty_dist = _(u"{distance:.3g}").format(distance=to_bugkiller) if to_bugkiller < 50.0 else _(u"{distance}").format(distance=int(to_bugkiller))
                return [
                    _(u"HIP 16613 ({}LY), Planet 1 A (1.4k LS), -11.0093 | -95.6755").format(pretty_dist),
                    _(u"Bring: advanced scanner, SRV."),
                    _(u"Scan the 3 COMMS Control of the crashed Anaconda, repeat."),
                ]
            else:
                pretty_dist = _(u"{distance:.3g}").format(distance=to_jameson) if to_jameson < 50.0 else _(u"{distance}").format(distance=int(to_jameson))
                return [
                    _(u"HIP 12099 ({}LY), Planet 1 B (1.1k LS), -54.3803 | -50.3575").format(pretty_dist),
                    _(u"Bring: advanced scanner, SRV."),
                    _(u"Crashed Cobra MK III with 4 COMMS Control, scannable from a fixed position."),
                ]
        
        if resource.lower() in ["classified scan fragment", "unusual encrypted files", "tagged encrypted codes", "specialized legacy firmware"]:
            distance = self.edr_systems.distance(reference_system, "Koli Discii")
            pretty_dist = _(u"{distance:.3g}").format(distance=distance) if distance < 50.0 else _(u"{distance}").format(distance=int(distance))
            return [
                _(u"Koli Discii ({}LY), Planet C 6 A (91k LS), 28.577 | 7.219").format(pretty_dist),
                _(u"Bring: advanced scanner, SRV."),
                _(u"Scan the 3 COMMS Control of the crashed Anaconda, repeat."), # TODO confirm the name of the things
            ]
        
        to_koli = self.edr_systems.distance(reference_system, "Koli Discii")
        to_hip = self.edr_systems.distance(reference_system, "HIP 16613")
        to_renet = self.edr_systems.distance(reference_system, "Renet")
        if resource.lower() in ["antimony", "tellurium", "ruthenium"] and to_renet < to_hip and to_renet < to_koli:
            what = _(u"Break the cargo rack of the crashed Anaconda, repeat.")
            pretty_dist = _(u"{distance:.3g}").format(distance=to_renet) if to_renet < 50.0 else _(u"{distance}").format(distance=int(to_renet))
            return [
                _(u"Renet ({}LY), Planet B 1 (378 LS), 14 | 135").format(pretty_dist),
                _(u"Bring: SRV."),
                what
            ]

        what = _(u"Scan the 3 COMMS Control of the crashed Anaconda, repeat.") if self.__is_data(resource) else _(u"Break the 3 cargo racks of the crashed Anaconda, repeat.")
            
        if to_hip < to_koli:
            pretty_dist = _(u"{distance:.3g}").format(distance=to_hip) if to_hip < 50.0 else _(u"{distance}").format(distance=int(to_hip))
            return [
                _(u"HIP 16613 ({}LY), Planet 1 A (1.4k LS), -11.0093 | -95.6755").format(pretty_dist),
                _(u"Bring: advanced scanner, SRV."),
                what
            ]
        
        pretty_dist = _(u"{distance:.3g}").format(distance=to_koli) if to_koli < 50.0 else _(u"{distance}").format(distance=int(to_koli))
        return [
            _(u"Koli Discii ({}LY), Planet C 6 A (91k LS), 28.577 | 7.219").format(pretty_dist),
            _(u"Bring: advanced scanner, SRV."),
            what
        ]

    def __is_data(self, resource):
        # Note: not exhaustive, only works for the anaconda case
        return resource in [ "adaptive encryptors capture", "atypical encryption archives", "modified consumer firmware",
                             "cracked industrial firmware", "specialized legacy firmware", "classified scan fragment",
                             "unusual encrypted files", "tagged encryption codes"]

    def from_surface_site(self, resource, reference_system, callback):
        to_research_5592 = self.edr_systems.distance(reference_system, "HR 5991")
        to_dav_hope = self.edr_systems.distance(reference_system, "Hyades Sector DR-V c2-23")
        if to_dav_hope < to_research_5592:
            return self.from_dav_hope(resource, reference_system, callback)
        else:
            return self.from_research_facility_5592(resource, reference_system, callback)
    
    def from_research_facility_5592(self, resource, reference_system, callback):
        distance = self.edr_systems.distance(reference_system, "HR 5991")
        pretty_dist = _(u"{distance:.3g}").format(distance=distance) if distance < 50.0 else _(u"{distance}").format(distance=int(distance))
        probabilities = {
            'chemical manipulators': 1.03125,
            'compound shielding': 0.75,
            'conductive polymers': 0.75,
            'heat vanes': 0.5625,
            'polymer capacitors': 0.65625,
            'refined focus crystals': 1.3125,
            'chemical distillery': 1.125,
            'classified scan databanks': 1.875,
            'conductive ceramics': 0.46875,
            'cracked industrial firmware': 0.1875,
            'electrochemical arrays': 0.65625,
            'focus crystals': 0.5625,
            'heat exchangers': 0.75,
            'shielding sensors': 1.03125,
        }

        probability = probabilities.get(resource.lower(), None)
        first_line = _(u"HR 5991 ({}LY), Planet 1 B (TODO LS), Research Facility 5592 at at 33.4701 | -2.1706").format(pretty_dist)
        if probability:
            first_line += _(u" {resource} @ {probability}%").format(resource=resource, probability=int(100*probability))
        alt_distance = self.edr_systems.distance(reference_system, "Hyades Sector DR-V c2-23")
        alt_pretty_dist = _(u"{distance:.3g}").format(distance=alt_distance) if alt_distance < 50.0 else _(u"{distance}").format(distance=int(alt_distance))
        return [
            first_line,
            _(u"Bring: advanced scanner, SRV."),
            _(u"Roam around to grab materials, repeat."),
            _(u"Alternative: 'Dav's hope' in Hyades Sector DR-V c2-23 ({}LY).").format(alt_pretty_dist)
        ]
    
    def from_dav_hope(self, resource, reference_system, callback):
        distance = self.edr_systems.distance(reference_system, "Hyades Sector DR-V c2-23")
        pretty_dist = _(u"{distance:.3g}").format(distance=distance) if distance < 50.0 else _(u"{distance}").format(distance=int(distance))
        probabilities = {
            "chemical manipulators": 1.286,
            "compound shielding": 0.744,
            "conductive polymers": 1.286,
            "configurable components": 1.000,
            "heat vanes": 1.000,
            "polymer capacitors": 1.286,
            "refined focus crystals": 0.857,
            "chemical distillery": 1.286,
            "classified scan databanks": 1.143,
            "conductive ceramics": 0.429,
            "cracked industrial firmware": 0.857,
            "electrochemical arrays": 0.714,
            "focus crystal": 1.143,
            "heat exchangers": 0.571,
            "high density composites": 3.000,
            "mechanical components": 1.286,
            "phase alloys": 1.286,
            "shielding sensors": 1.286,
        }

        probability = probabilities.get(resource.lower(), None)
        first_line = _(u"Hyades Sector DR-V c2-23 ({}LY), Planet A 5 (60 LS), Dav's Hope at 44.8180 | -31.3893").format(pretty_dist)
        if probability:
            first_line += _(u" {resource} @ {probability}%").format(resource=resource, probability=int(100*probability))
        return [
            first_line,
            _(u"Bring: advanced scanner, SRV."),
            _(u"Roam around to grab materials, repeat."),
            _(u"Search online for 'Dav's hope map' to find out which spots drop {}.").format(resource)
        ]

    def from_isinor(self, resource, reference_system, callback):
        alternative = None
        if resource == "peculiar shield frequency data":
            alternative = _(u"Alt: scan combat/pirate (RES) ships, hack mega-ships.")
        elif resource == "unexpected emission data":
            alternative = _(u"Alt: scan combat/pirate (RES)/authority (CZ) ships, private data beacons in USS - Encoded Emissions.")
        elif resource == "untypical shield scans":
            alternative = _(u"Alt: combat/pirate (RES)/authority (CZ) ships.")
        elif resource == "aberrant shield pattern analysis":
            alternative = _(u"Alt: scan combat/pirate (RES) ships.")

        distance = self.edr_systems.distance(reference_system, "Isinor")
        pretty_dist = _(u"{distance:.3g}").format(distance=distance) if distance < 50.0 else _(u"{distance}").format(distance=int(distance))
        return [
            _(u"Isinor ({}LY), Planet A 5 (60 LS), Permit locked (missions or exploration data for 'Chapter of Isinor')").format(pretty_dist),
            _(u"Bring: permit, decent shields"),
            _(u"Drop on 'Unauthorised Installation' or 'Convoy beacon', scan ships, repeat."),
            alternative
        ]

    def state_dependent_resource(self, resource, reference_system, callback):
        if resource is None or reference_system is None:
            return False

        if not (self.edr_systems.in_bubble(reference_system) or self.edr_systems.in_colonia(reference_system)):
            return False
 
        checker = None
        if resource == "core dynamics composites":
            checker = edrstatecheck.EDRCoreDynamicsCompositesCheck()
        elif resource == "imperial shielding":
            checker = edrstatecheck.EDRImperialShieldingCheck()
        elif resource == "improvised components":
            checker = edrstatecheck.EDRImprovisedComponentsCheck()
        elif resource == "military grade alloys":
            checker = edrstatecheck.EDRMilitaryGradeAlloysCheck()
        elif resource == "military supercapacitors":
            checker = edrstatecheck.EDRMilitarySupercapacitorsCheck()
        elif resource == "pharmaceutical isolators":
            checker = edrstatecheck.EDRPharmaceuticalIsolatorsCheck()
        elif resource == "proto light alloys":
            checker = edrstatecheck.EDRProtoLightAlloysCheck()
        elif resource == "proto radiolic alloys":
            checker = edrstatecheck.EDRProtoRadiolicAlloysCheck()
        elif resource == "proto heat radiators":
            checker = edrstatecheck.EDRProtoHeatRadiatorCheck()
        elif resource == "proprietary composites":
            checker = edrstatecheck.EDRProprietaryCompositesCheck()
        elif resource == "datamined wake exceptions":
            checker = edrstatecheck.EDRDataminedWakeExceptionsCheck()
        elif resource == 'polymer capacitors':
            checker = edrstatecheck.EDRPolymerCapacitorsCheck()
        else:
            return False
        
        finder = edrstatefinder.EDRStateFinder(reference_system, checker, self.edr_systems, callback)
        finder.within_radius(min(60, self.radius))
        finder.permits_in_possesion(self.permits)
        finder.start()

        return True

    def from_combat_authority_scans_encoded_emissions(self, resource, reference_system, callback):
        return [
            _(u"Scan combat or authority ships, e.g. pirates in RES, military ships in CZ."),
            _(u"Scan private data beacons found in 'Encoded Emissions' sources")
        ]

    def mat_trader_mining_all(self, resource, reference_system, callback):
        return  [
            _(u"Can be found by mining asteroids in planet rings."),
            _(u"More efficient: exchange other materials at a raw material trader, send !raw to find the closest one.")
        ] 


    def recommend_prospecting_planet(self, resource, reference_system, callback):
        planets_lut = {
            'polonium': [ {'name': 'HIP 59646', 'planet': '1', 'concentration':	0.013, 'gravity': 1.35, 'distanceToArrival': 66},
                          {'name': 'Tiris', 'planet': '1 c', 'concentration': 0.012, 'gravity': 0.13, 'distanceToArrival': 17},
                          {'name': 'LTT 6705', 'planet': 'A 2', 'concentration': 0.012, 'gravity': 0.93, 'distanceToArrival': 25},
                          {'name': 'HIP 22286', 'planet': '2', 'concentration': 0.013, 'gravity': 1.49, 'distanceToArrival': 16}
            ],
            'technetium': [ {'name': 'HIP 108602', 'planet': 'B 2', 'concentration': 0.015, 'gravity': 0.10, 'distanceToArrival': 468},
                            {'name': 'Kadaren', 'planet': '2', 'concentration':	0.015, 'gravity': 1.23, 'distanceToArrival': 26},
                            {'name': 'Nihal', 'planet': '1', 'concentration': 0.014, 'gravity': 1.29, 'distanceToArrival': 335}
            ],
            'yttrium':    [ {'name': 'Mse', 'planet': 'B 1', 'concentration': 0.026, 'gravity': 0.29, 'distanceToArrival': 962},
                            {'name': 'Epsilon Ceti', 'planet': 'A 1', 'concentration':	0.025, 'gravity': 1.92, 'distanceToArrival': 85},
                            {'name': 'Hip 20485', 'planet': 'A 1', 'concentration': 0.025, 'gravity': 0.24, 'distanceToArrival': 11}
            ],
            'cadmium':    [ {'name': 'Anca', 'planet': 'A 1', 'concentration': 0.033, 'gravity': 0.09, 'distanceToArrival': 6},
                            {'name': 'Tiris', 'planet': '1 C', 'concentration':	0.033, 'gravity': 0.13, 'distanceToArrival': 17},
                            {'name': 'Col 285 Sector SU-E c12-23', 'planet': '1', 'concentration': 0.037, 'gravity': 1.5, 'distanceToArrival': 9}
            ],
            'mercury':    [ {'name': 'Mse', 'planet': 'B 1', 'concentration': 0.019, 'gravity': 0.29, 'distanceToArrival': 962},
                            {'name': 'Kadaren', 'planet': '2', 'concentration':	0.018, 'gravity': 1.23, 'distanceToArrival': 26},
                            {'name': 'Clota', 'planet': '1', 'concentration': 0.019, 'gravity': 1.51, 'distanceToArrival': 12},
                            {'name': 'HIP 22286', 'planet': '2', 'concentration': 0.019, 'gravity': 1.49, 'distanceToArrival': 16}
            ],
            'selenium':   [ {'name': 'LHS 417', 'planet': '9 E A', 'concentration': 0.049, 'gravity': 0.03, 'distanceToArrival': 3776},
                            {'name': 'Jeng', 'planet': 'A 1 D A', 'concentration':	0.049, 'gravity': 0.03, 'distanceToArrival': 828},
                            {'name': 'Kandanda', 'planet': '3 D A', 'concentration': 0.048, 'gravity': 0.03, 'distanceToArrival': 2548}
            ],
            'tin':        [ {'name': '102 Iota Tauri', 'planet': 'B 2 A', 'concentration': 0.03, 'gravity': 0.19, 'distanceToArrival': 3776},
                            {'name': 'Nu Tauri', 'planet': '1', 'concentration':	0.029, 'gravity': 2.29, 'distanceToArrival': 828},
                            {'name': 'Col 285 Sector SU-E c12-23', 'planet': '1', 'concentration': 0.031, 'gravity': 1.5, 'distanceToArrival': 2548},
                            {'name': 'Dhakhan', 'planet': 'C 2', 'concentration': 0.028, 'gravity': 0.08, 'distanceToArrival': 13361},
                            {'name': 'HIP 22286', 'planet': '2', 'concentration': 0.029, 'gravity': 1.49, 'distanceToArrival': 16}
            ],
            'arsenic':    [ {'name': 'Masszony', 'planet': '1 A A', 'concentration': 0.029, 'gravity': 0.09, 'distanceToArrival': 2114},
                            {'name': 'HIP 15304', 'planet': '6 C A', 'concentration':	0.029, 'gravity': 0.06, 'distanceToArrival': 3601},
                            {'name': 'El Tio', 'planet': '3 E A', 'concentration':	0.029, 'gravity': 0.05, 'distanceToArrival':1142 },
                            {'name': 'Col 285 Sector SU-E c12-23', 'planet': '1', 'concentration': 0.022, 'gravity': 1.5, 'distanceToArrival': 2548},
                            {'name': 'Hyades Sector DR-V c2-23', 'planet': 'A 3', 'concentration': 0.024, 'gravity': 0.08, 'distanceToArrival': 23}
            ],
            'molybdenum': [ {'name': 'Mse', 'planet': 'B 1', 'concentration': 0.028, 'gravity': 0.29, 'distanceToArrival': 962},
                            {'name': 'Tiris', 'planet': '1 c', 'concentration': 0.028, 'gravity': 0.13, 'distanceToArrival': 17},
                            {'name': 'Hip 20485', 'planet': 'A 1', 'concentration': 0.028, 'gravity': 0.24, 'distanceToArrival': 11}
            ],
            'niobium':    [ {'name': '102 Iota Tauri', 'planet': 'B 2 A', 'concentration': 0.03, 'gravity': 0.19, 'distanceToArrival': 3776},
                            {'name': 'LTT 6705', 'planet': 'A 2', 'concentration': 0.029, 'gravity': 0.93, 'distanceToArrival': 25},
                            {'name': 'Alpha Chamaelontis', 'planet': 'B 1 A', 'concentration': 0.029, 'gravity': 0.13, 'distanceToArrival': 1786},
            ],
            'chromium':   [ {'name': 'CPD-60 604', 'planet': 'B 1', 'concentration': 0.175, 'gravity': 0.32, 'distanceToArrival': 157},
                            {'name': 'Aurgel', 'planet': 'B 1', 'concentration': 0.177, 'gravity': 0.74, 'distanceToArrival': 9},
                            {'name': 'HIP 27123', 'planet': 'A 1', 'concentration': 0.182, 'gravity': 0.45, 'distanceToArrival': 54},
            ],
            'germanium':  [ {'name': 'Vega', 'planet': '2 D A', 'concentration': 0.062, 'gravity': 0.10, 'distanceToArrival': 1801},
                            {'name': 'HIP 113858', 'planet': '4 B A', 'concentration': 0.063, 'gravity': 0.09, 'distanceToArrival': 3055},
                            {'name': 'Ernueken', 'planet': '7 F A', 'concentration': 0.063, 'gravity': 0.06, 'distanceToArrival': 2597},
            ],
            'manganese':  [ {'name': 'LTT 8419', 'planet': 'A 1 A', 'concentration': 0.163, 'gravity': 0.18, 'distanceToArrival': 25},
                            {'name': 'Kadaren', 'planet': '2', 'concentration':	0.171, 'gravity': 1.23, 'distanceToArrival': 26},
                            {'name': 'HIP 48141', 'planet': 'C 1 A', 'concentration': 0.165, 'gravity': 0.06, 'distanceToArrival': 180},
            ],
            'vanadium':   [ {'name': '102 Iota Tauri', 'planet': 'B 2 A', 'concentration': 0.109, 'gravity': 0.19, 'distanceToArrival': 3776},
                            {'name': 'Nu Tauri', 'planet': '1', 'concentration':	0.109, 'gravity': 2.29, 'distanceToArrival': 828},
                            {'name': 'Clota', 'planet': '1', 'concentration': 0.107, 'gravity': 1.51, 'distanceToArrival': 12},
                            {'name': 'Dhakhan', 'planet': 'C 2', 'concentration': 0.105, 'gravity': 0.08, 'distanceToArrival': 13361},
                            {'name': 'HIP 22286', 'planet': '2', 'concentration': 0.109, 'gravity': 1.49, 'distanceToArrival': 16}
            ],
            'zinc':       [ {'name': 'LTT 6705', 'planet': 'A 2', 'concentration': 0.115, 'gravity': 0.93, 'distanceToArrival': 25},
                            {'name': 'Alpha Chamaelontis', 'planet': 'B 1 A', 'concentration': 0.114, 'gravity': 0.13, 'distanceToArrival': 1786},
                            {'name': 'Epsilon Ceti', 'planet': 'A 1', 'concentration':	0.113, 'gravity': 1.92, 'distanceToArrival': 85},
            ],
        }

        candidates = planets_lut.get(resource, None)
        if not candidates:
            return False

        best_distance = None
        best = None
        for planet in candidates:
            distance = self.edr_systems.distance(reference_system, planet['name'])
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best = planet
        
        pretty_dist = _(u"{distance:.3g}").format(distance=best_distance) if best_distance < 50.0 else _(u"{distance}").format(distance=int(best_distance))
        return [
            _(u'{} ({}LY), Planet {} ({}LS, {}G), {} @ {}%').format(best['name'], pretty_dist, best['planet'], best['distanceToArrival'], best['gravity'], resource, int(100*best['concentration'])),
            _(u"Bring: advanced scanner, SRV."),
            _(u"Break some rocks. Higher chances of Very Rare and Rare resources in metallic meteorite, metallic outcrop and mesosiderite.")
        ]

    def from_hacking(self, resource, reference_system, callback):
        pois = {
            'Atins': {'name': 'Atins', 'loc': 'Scientific Installation near Planet 1', 'bring': _(u"Bring: 2 recon controllers, limpets, silent running ship."), 'what': _(u'Scan the installation, then the Comms array. Hack it. Run silent before the hacking begins / ends, avoid scans. Repeat.'), 'distanceToArrival': 11},
            'Kemurukamar': {'name': 'Kemurukamar', 'loc': 'Pirate Cove near Planet A 1', 'bring': _(u"Bring: 2-3 recon controllers, limpets, silent running ship."), 'what': _(u"Scan the stranded mega-ship 'Blazin’ Dynamo', then the Comms and Data arrays. Hack them. Run silent before the hacking begins / ends, avoid scans. Repeat."), 'distanceToArrival': 1913},
        }

        alts = {
            "modified embedded firmware": _(u'Alt: scans of data points at L3M / M3M / M4M settlements. Installation, mega-ships. Mission rewards.'),
            "divergent scan data":  _(u"Alt: scans of data points at settlements, authority/military ships, data beacons in 'Encoded Emissions', satellites. Installations, mega-ships. Mission rewards."),
            "security firmware patch":  _(u'Alt: scans of data points at M4M / L3M / M2M settlements. Installations, mega-ships.'),
            "open symmetric keys":  _(u"Alt: scans of data points at M5M / L2M / M2M settlements, data beacons in 'Encoded Emissions', satellites. Installations, mega-ships."),
            "classified scan databanks": _(u"Alt: scans of data points at M4L / M1L / M3L settlements, haulage ships. Installation, mega-ships."),
        }

        hacking_poi_lut = {
            "modified embedded firmware": [
                {'poi': 'Atins', 'probability': 0.343},
                {'poi': 'Kemurukamar', 'probability': 3.000},
            ],
            "divergent scan data": [
                {'poi': 'Atins', 'probability': 0.343},
                {'poi': 'Kemurukamar', 'probability': 3.273},
            ],
            "security firmware patch": [
                {'poi': 'Atins', 'probability': 0.171},
                {'poi': 'Kemurukamar', 'probability': 3.545},
            ],
            "open symmetric keys": [
                {'poi': 'Atins', 'probability': 0.171},
                {'poi': 'Kemurukamar', 'probability': 2.182},
            ],
            "classified scan databank": [
                {'poi': 'Atins', 'probability': 0.643},
                {'poi': 'Kemurukamar', 'probability': 3.818},
            ],
        }

        '''
        TODO
        Blazin'Dynamo at Kemurukamar
        Peculiar Shield Frequency Data	g5	0.545
        Classified Scan Fragment	g5	1.364
        Aberrant Shield Pattern Analysis	g4	0.818
        Cracked Industrial Firmware	g3	4.636
        Untypical Shield Scans	g3	2.182
        '''

        candidates = hacking_poi_lut.get(resource, None)
        if not candidates:
            return False

        best_distance = None
        best = None
        for candidate in candidates:
            distance = self.edr_systems.distance(reference_system, candidate['poi'])
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best = candidate
        
        pretty_dist = _(u"{distance:.3g}").format(distance=best_distance) if best_distance < 50.0 else _(u"{distance}").format(distance=int(best_distance))
        poi = pois[best['poi']]

        if best.get('gravity', None):
            return [
                _(u'{} ({}LY), {} ({}LS, {}G), {} @ {}%').format(poi['name'], pretty_dist, poi['loc'], poi['distanceToArrival'], poi['gravity'], resource, int(100*best['probability'])),
                poi['bring'],
                poi['what'],
                alts[resource]
            ]
        else:
            return [
                _(u'{} ({}LY), {} ({}LS), {} @ {}%').format(poi['name'], pretty_dist, poi['loc'], poi['distanceToArrival'], resource, int(100*best['probability'])),
                poi['bring'],
                poi['what'],
                alts[resource]
            ]


    def from_high_energy_wakes(self, resource, reference_system, callback):
        return [
            _(u'Captured by scanning high energy wakes.'),
            _(u'Higher chances in high population (high traffic) systems')
        ]

    def noteworthy_facts(self, fsdjump_event):
        state = ''
        if "FactionState" not in fsdjump_event:
            # New multi-states BGS in 3.3...
            factions = fsdjump_event.get('Factions', [])
            dominant_faction = fsdjump_event.get('SystemFaction', None)
            for faction in factions:
                if faction["Name"] == dominant_faction:
                    state = faction["FactionState"]
                    break
        else:
            state = fsdjump_event['FactionState'].lower()
        
        
        if state not in ['outbreak', 'war', 'boom', 'civil unrest', 'war', 'civil war', 'famine', 'election', 'none']:
            return None 

        noteworthy = []
        chance = ''
        allegiance = fsdjump_event.get('SystemAllegiance', '').lower()
        security = fsdjump_event.get('SystemSecurity', '')
        population = fsdjump_event.get('Population', 0)

        if population >= 1000000:
            chance += '+' * int(max(3, math.log10(population / 100000)))
        
        chance += '+'
        if state == 'outbreak':
            if allegiance in ['alliance', 'independent'] or security == '$GAlAXY_MAP_INFO_state_anarchy;':
                chance += '+'
            elif allegiance == 'empire':
                lchance = '+'
                if population >= 1000000:
                    lchance += '+' * int(max(3, math.log10(population / 100000)))
                noteworthy.append(_(u'Imperial Shielding (USS-HGE, {})').format(lchance))
            noteworthy.append(_(u'Pharmaceutical Isolators (USS-HGE, {})').format(chance))
        elif state == ['none', 'election']:
            if allegiance == 'empire':
                lchance = chance
                lchance += '+'
                noteworthy.append(_(u'Imperial Shielding (USS-HGE, {})').format(lchance))
            if allegiance == 'federation':
                lchance = chance
                lchance += '+'
                noteworthy.append(_(u'Core Dynamics Composites (USS-HGE, {})').format(lchance))                
            if state == 'election' and allegiance in ['federation', 'empire']:
                noteworthy.append(_(u'Proprietary Composites (USS-HGE, {})').format(chance))
        elif state == 'boom':
            noteworthy.append(_(u'Exquisite Focus Crystals (Mission rewards, {})').format(chance))
            if allegiance in ['alliance', 'independent']:
                chance += '+'
            noteworthy.append(_(u'Proto Light Alloys (USS-HGE, {})').format(chance))
            noteworthy.append(_(u'Proto Heat Radiator (USS-HGE, {})').format(chance))
            noteworthy.append(_(u'Proto Radiolic Alloys (USS-HGE, {})').format(chance))
        elif state == 'civil unrest':
            if allegiance in ['alliance', 'independent']:
                chance += '+'
            noteworthy.append(_(u'Improvised Components (USS-HGE, {})').format(chance))
        elif state in ['war', 'civil war']:
            if allegiance in ['alliance', 'independent'] or security == '$GAlAXY_MAP_INFO_state_anarchy;':
                chance += '+'
            noteworthy.append(_(u'Military Grade Alloy (USS-HGE, {})').format(chance))
            noteworthy.append(_(u'Military Supercapacitors (USS-HGE, {})').format(chance))
        elif state == 'famine':
            noteworthy.append(_(u'Datamined Wake Exception (Distribution Center, {})').format(chance))

        return noteworthy
