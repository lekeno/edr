# coding= utf-8
from __future__ import absolute_import

import math
import json
import os
import random

from clippy import copy
from edrfactions import EDRFactions, EDRFaction
import edrstatecheck
from edrstatefinder import EDRStateFinder
from edri18n import _
from edrrawdepletables import EDRRawDepletables
import utils2to3

class EDRResourceFinder(object):

    RAW_MATS = json.loads(open(utils2to3.abspathmaker(__file__, 'data', 'raw.json')).read())

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
        "painite": "pai",
        "bromellite": "bro",
        "low temperature diamonds": "l t d",
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
        "ltd": "low temperature diamonds", "l t d": "low temperature diamonds", "low temperature diamond": "low temperature diamonds",
        "pain": "painite", "pai": "painite",
        "brom": "bromellite", "bro": "bromellite",
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
        "tellurium": 'recommend_planet_or_crashed_site_or_depletable', "ruthenium": 'recommend_planet_or_crashed_site_or_depletable', "tungsten": 'recommend_crashed_site_or_depletable',
        "antimony": 'recommend_planet_or_crashed_site_or_depletable',
        "zirconium": 'recommend_crashed_site_or_depletable', "adaptive encryptors capture": 'recommend_crashed_site',
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
        "polonium": 'recommend_prospecting_planet', "technetium": 'recommend_planet_or_depletable', "yttrium": 'recommend_planet_or_depletable', "cadmium": 'recommend_planet_or_depletable', "mercury": 'recommend_planet_or_depletable', "selenium": 'recommend_planet_or_depletable', "tin": 'recommend_planet_or_depletable',
        "arsenic": 'recommend_planet_or_depletable', "molybdenum": 'recommend_planet_or_depletable',
        "niobium": 'recommend_planet_or_depletable', "chromium": 'recommend_planet_or_depletable',
        "vanadium": 'recommend_planet_or_depletable', "zinc": 'recommend_planet_or_depletable',
        "germanium": 'recommend_planet_or_depletable', "manganese": 'recommend_planet_or_depletable',
        "painite": 'recommend_prospecting_ring',
        "bromellite": 'recommend_prospecting_ring',
        "low temperature diamonds": 'recommend_prospecting_ring',
        "boron": 'mat_trader_mining_all',
        "ambiguous abbreviation (pc)": "ambiguous_p_c",
        "ambiguous abbreviation (cc)": "ambiguous_c_c",
    }

    def __init__(self, edr_systems, permits = []):
        self.edr_systems = edr_systems
        self.edr_factions = EDRFactions()
        self.radius = 50
        self.permits = permits

    def persist(self):
        self.edr_factions.persist()

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
    
    def recommend_crashed_site_or_depletable(self, resource, reference_system, callback):
        suggestion = None
        if random.random() < 0.5:
            suggestion = self.recommend_raw_depletable(resource, reference_system, callback)
        if not suggestion:
            suggestion = self.recommend_crashed_site(resource, reference_system, callback)
        return suggestion

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
                copy("HIP 16613")
                return [
                    _(u"HIP 16613 ({}LY), Planet 1 A (1.4k LS), -11.0093 | -95.6755").format(pretty_dist),
                    _(u"Bring: advanced scanner, SRV."),
                    _(u"Scan the 3 COMMS Control of the crashed Anaconda, repeat."),
                ]
            else:
                pretty_dist = _(u"{distance:.3g}").format(distance=to_jameson) if to_jameson < 50.0 else _(u"{distance}").format(distance=int(to_jameson))
                copy("HIP 12099")
                return [
                    _(u"HIP 12099 ({}LY), Planet 1 B (1.1k LS), -54.3803 | -50.3575").format(pretty_dist),
                    _(u"Bring: advanced scanner, SRV."),
                    _(u"Crashed Cobra MK III with 4 COMMS Control, scannable from a fixed position."),
                ]
        
        if resource.lower() in ["classified scan fragment", "unusual encrypted files", "tagged encrypted codes", "specialized legacy firmware"]:
            distance = self.edr_systems.distance(reference_system, "Koli Discii")
            pretty_dist = _(u"{distance:.3g}").format(distance=distance) if distance < 50.0 else _(u"{distance}").format(distance=int(distance))
            copy("Koli Discii")
            return [
                _(u"Koli Discii ({}LY), Planet C 6 A (91k LS), 28.577 | 7.219").format(pretty_dist),
                _(u"Bring: advanced scanner, SRV."),
                _(u"Scan the 3 COMMS Control of the crashed Anaconda, repeat."), # TODO confirm the name of the things
            ]
        
        to_koli = self.edr_systems.distance(reference_system, "Koli Discii")
        to_hip = self.edr_systems.distance(reference_system, "HIP 16613")
        to_renet = self.edr_systems.distance(reference_system, "Renet")
        to_thoth = self.edr_systems.distance(reference_system, "Thoth")
        if resource.lower() in ["antimony", "tellurium", "ruthenium"]:
            if to_renet < to_hip and to_renet < to_koli and to_renet < to_thoth:
                what = _(u"Break the cargo rack of the crashed Anaconda, repeat.")
                pretty_dist = _(u"{distance:.3g}").format(distance=to_renet) if to_renet < 50.0 else _(u"{distance}").format(distance=int(to_renet))
                copy("Renet")
                return [
                    _(u"Renet ({}LY), Planet B 1 (378 LS), 14 | 135").format(pretty_dist),
                    _(u"Bring: SRV."),
                    what
                ]
            elif to_thoth < to_hip and to_thoth < to_koli and to_thoth < to_renet:
                what = _(u"Break the cargo rack of the crashed Anaconda, repeat.")
                pretty_dist = _(u"{distance:.3g}").format(distance=to_renet) if to_thoth < 50.0 else _(u"{distance}").format(distance=int(to_thoth))
                copy("Thoth")
                return [
                    _(u"Thoth ({}LY), Planet 1 A (69 LS), -2.77 | 16.67").format(pretty_dist),
                    _(u"Bring: SRV."),
                    what
                ]

        what = _(u"Scan the 3 COMMS Control of the crashed Anaconda, repeat.") if self.__is_data(resource) else _(u"Break the 3 cargo racks of the crashed Anaconda, repeat.")
            
        if to_hip < to_koli:
            pretty_dist = _(u"{distance:.3g}").format(distance=to_hip) if to_hip < 50.0 else _(u"{distance}").format(distance=int(to_hip))
            copy("HIP 16613")
            return [
                _(u"HIP 16613 ({}LY), Planet 1 A (1.4k LS), -11.0093 | -95.6755").format(pretty_dist),
                _(u"Bring: advanced scanner, SRV."),
                what
            ]
        
        pretty_dist = _(u"{distance:.3g}").format(distance=to_koli) if to_koli < 50.0 else _(u"{distance}").format(distance=int(to_koli))
        copy("Koli Discii")
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
        first_line = _(u"HR 5991 ({}LY), Planet 1 B (2180 LS), Research Facility 5592 at 33.4701 | -2.1706").format(pretty_dist)
        if probability:
            first_line += _(u" {resource} @ {probability}%").format(resource=resource, probability=int(100*probability))
        alt_distance = self.edr_systems.distance(reference_system, "Hyades Sector DR-V c2-23")
        alt_pretty_dist = _(u"{distance:.3g}").format(distance=alt_distance) if alt_distance < 50.0 else _(u"{distance}").format(distance=int(alt_distance))
        copy("HR 5991")
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
        copy("Hyades Sector DR-V c2-23")
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
        copy("Isinor")
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
        
        finder = EDRStateFinder(reference_system, checker, self.edr_systems, callback)
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
    
    def recommend_planet_or_crashed_site_or_depletable(self, resource, reference_system, callback):
        suggestion = None
        r = random.random()
        if r < 0.3333:
            suggestion = self.recommend_raw_depletable(resource, reference_system, callback)
        if not suggestion and (r >= 0.3333 and r < 0.6666):
            suggestion = self.recommend_prospecting_planet(resource, reference_system, callback)
        if not suggestion or r >= 0.6666:
            suggestion = self.recommend_crashed_site(resource, reference_system, callback)            
        return suggestion

    def recommend_planet_or_depletable(self, resource, reference_system, callback):
        suggestion = None
        if random.random() < 0.5:
            suggestion = self.recommend_raw_depletable(resource, reference_system, callback)
        if not suggestion:
            suggestion = self.recommend_prospecting_planet(resource, reference_system, callback)
        return suggestion


    def recommend_prospecting_planet(self, resource, reference_system, callback):
        planets_lut = {
            'tellurium': [ { 'name': 'HIP 36601', 'planet': 'C 3 b', 'gravity': 0.04, 'distanceToArrival': 153683, 'type': 'crystals'}],
            'ruthenium': [{ 'name': 'HIP 36601', 'planet': 'C 1 d', 'gravity': 0.08, 'distanceToArrival': 154104, 'type': 'crystals'}
            ],
            'antimony': [ { 'name': 'Outotz LS-K D8-3', 'planet': 'B 5 c', 'gravity': 0.07, 'distanceToArrival': 310673, 'type': 'crystals'}],
            'polonium': [ {'name': 'HIP 59646', 'planet': '1', 'concentration':	0.013, 'gravity': 1.35, 'distanceToArrival': 66, 'type': 'rocks'},
                          {'name': 'Tiris', 'planet': '1 c', 'concentration': 0.012, 'gravity': 0.13, 'distanceToArrival': 17, 'type': 'rocks'},
                          {'name': 'LTT 6705', 'planet': 'A 2', 'concentration': 0.012, 'gravity': 0.93, 'distanceToArrival': 25, 'type': 'rocks'},
                          {'name': 'HIP 22286', 'planet': '2', 'concentration': 0.013, 'gravity': 1.49, 'distanceToArrival': 16, 'type': 'rocks'},
                          { 'name': 'HIP 36601', 'planet': 'C 1 a', 'gravity': 0.09, 'distanceToArrival': 154099, 'type': 'crystals'}
            ],
            'technetium': [ {'name': 'HIP 108602', 'planet': 'B 2', 'concentration': 0.015, 'gravity': 0.10, 'distanceToArrival': 468, 'type': 'rocks'},
                            {'name': 'Kadaren', 'planet': '2', 'concentration':	0.015, 'gravity': 1.23, 'distanceToArrival': 26, 'type': 'rocks'},
                            {'name': 'Nihal', 'planet': '1', 'concentration': 0.014, 'gravity': 1.29, 'distanceToArrival': 335, 'type': 'rocks'},
                            { 'name': 'HIP 36601', 'planet': 'C 5 a', 'gravity': 0.03, 'distanceToArrival': 154093, 'type': 'crystals'}
            ],
            'yttrium':    [ {'name': 'Mse', 'planet': 'B 1', 'concentration': 0.026, 'gravity': 0.29, 'distanceToArrival': 962, 'type': 'rocks'},
                            {'name': 'Epsilon Ceti', 'planet': 'A 1', 'concentration':	0.025, 'gravity': 1.92, 'distanceToArrival': 85, 'type': 'rocks'},
                            {'name': 'Hip 20485', 'planet': 'A 1', 'concentration': 0.025, 'gravity': 0.24, 'distanceToArrival': 11, 'type': 'rocks'},
                            { 'name': 'Outotz LS-K D8-3', 'planet': 'B 5 a', 'gravity': 0.09, 'distanceToArrival': 310675, 'type': 'crystals'}
            ],
            'cadmium':    [ {'name': 'Anca', 'planet': 'A 1', 'concentration': 0.033, 'gravity': 0.09, 'distanceToArrival': 6, 'type': 'rocks'},
                            {'name': 'Tiris', 'planet': '1 C', 'concentration':	0.033, 'gravity': 0.13, 'distanceToArrival': 17, 'type': 'rocks'},
                            {'name': 'Col 285 Sector SU-E c12-23', 'planet': '1', 'concentration': 0.037, 'gravity': 1.5, 'distanceToArrival': 9, 'type': 'rocks'}
            ],
            'mercury':    [ {'name': 'Mse', 'planet': 'B 1', 'concentration': 0.019, 'gravity': 0.29, 'distanceToArrival': 962, 'type': 'rocks'},
                            {'name': 'Kadaren', 'planet': '2', 'concentration':	0.018, 'gravity': 1.23, 'distanceToArrival': 26, 'type': 'rocks'},
                            {'name': 'Clota', 'planet': '1', 'concentration': 0.019, 'gravity': 1.51, 'distanceToArrival': 12, 'type': 'rocks'},
                            {'name': 'HIP 22286', 'planet': '2', 'concentration': 0.019, 'gravity': 1.49, 'distanceToArrival': 16, 'type': 'rocks'}
            ],
            'selenium':   [ {'name': 'LHS 417', 'planet': '9 E A', 'concentration': 0.049, 'gravity': 0.03, 'distanceToArrival': 3776, 'type': 'rocks'},
                            {'name': 'Jeng', 'planet': 'A 1 D A', 'concentration':	0.049, 'gravity': 0.03, 'distanceToArrival': 828, 'type': 'rocks'},
                            {'name': 'Kandanda', 'planet': '3 D A', 'concentration': 0.048, 'gravity': 0.03, 'distanceToArrival': 2548, 'type': 'rocks'},
                            # TODO CPD-51 3323 planet 1 D A Crystalline fragments for selenium
            ],
            'tin':        [ {'name': '102 Iota Tauri', 'planet': 'B 2 A', 'concentration': 0.03, 'gravity': 0.19, 'distanceToArrival': 3776, 'type': 'rocks'},
                            {'name': 'Nu Tauri', 'planet': '1', 'concentration':	0.029, 'gravity': 2.29, 'distanceToArrival': 828, 'type': 'rocks'},
                            {'name': 'Col 285 Sector SU-E c12-23', 'planet': '1', 'concentration': 0.031, 'gravity': 1.5, 'distanceToArrival': 2548, 'type': 'rocks'},
                            {'name': 'Dhakhan', 'planet': 'C 2', 'concentration': 0.028, 'gravity': 0.08, 'distanceToArrival': 13361, 'type': 'rocks'},
                            {'name': 'HIP 22286', 'planet': '2', 'concentration': 0.029, 'gravity': 1.49, 'distanceToArrival': 16, 'type': 'rocks'}
            ],
            'arsenic':    [ {'name': 'Masszony', 'planet': '1 A A', 'concentration': 0.029, 'gravity': 0.09, 'distanceToArrival': 2114, 'type': 'rocks'},
                            {'name': 'HIP 15304', 'planet': '6 C A', 'concentration':	0.029, 'gravity': 0.06, 'distanceToArrival': 3601, 'type': 'rocks'},
                            {'name': 'El Tio', 'planet': '3 E A', 'concentration':	0.029, 'gravity': 0.05, 'distanceToArrival':1142, 'type': 'rocks'},
                            {'name': 'Col 285 Sector SU-E c12-23', 'planet': '1', 'concentration': 0.022, 'gravity': 1.5, 'distanceToArrival': 2548, 'type': 'rocks'},
                            {'name': 'Hyades Sector DR-V c2-23', 'planet': 'A 3', 'concentration': 0.024, 'gravity': 0.08, 'distanceToArrival': 23, 'type': 'rocks'}
            ],
            'molybdenum': [ {'name': 'Mse', 'planet': 'B 1', 'concentration': 0.028, 'gravity': 0.29, 'distanceToArrival': 962, 'type': 'rocks'},
                            {'name': 'Tiris', 'planet': '1 c', 'concentration': 0.028, 'gravity': 0.13, 'distanceToArrival': 17, 'type': 'rocks'},
                            {'name': 'Hip 20485', 'planet': 'A 1', 'concentration': 0.028, 'gravity': 0.24, 'distanceToArrival': 11, 'type': 'rocks'}
            ],
            'niobium':    [ {'name': '102 Iota Tauri', 'planet': 'B 2 A', 'concentration': 0.03, 'gravity': 0.19, 'distanceToArrival': 3776, 'type': 'rocks'},
                            {'name': 'LTT 6705', 'planet': 'A 2', 'concentration': 0.029, 'gravity': 0.93, 'distanceToArrival': 25, 'type': 'rocks'},
                            {'name': 'Alpha Chamaelontis', 'planet': 'B 1 A', 'concentration': 0.029, 'gravity': 0.13, 'distanceToArrival': 1786, 'type': 'rocks'},
            ],
            'chromium':   [ {'name': 'CPD-60 604', 'planet': 'B 1', 'concentration': 0.175, 'gravity': 0.32, 'distanceToArrival': 157, 'type': 'rocks'},
                            {'name': 'Aurgel', 'planet': 'B 1', 'concentration': 0.177, 'gravity': 0.74, 'distanceToArrival': 9, 'type': 'rocks'},
                            {'name': 'HIP 27123', 'planet': 'A 1', 'concentration': 0.182, 'gravity': 0.45, 'distanceToArrival': 54, 'type': 'rocks'},
            ],
            'germanium':  [ {'name': 'Vega', 'planet': '2 D A', 'concentration': 0.062, 'gravity': 0.10, 'distanceToArrival': 1801, 'type': 'rocks'},
                            {'name': 'HIP 113858', 'planet': '4 B A', 'concentration': 0.063, 'gravity': 0.09, 'distanceToArrival': 3055, 'type': 'rocks'},
                            {'name': 'Ernueken', 'planet': '7 F A', 'concentration': 0.063, 'gravity': 0.06, 'distanceToArrival': 2597, 'type': 'rocks'},
            ],
            'manganese':  [ {'name': 'LTT 8419', 'planet': 'A 1 A', 'concentration': 0.163, 'gravity': 0.18, 'distanceToArrival': 25, 'type': 'rocks'},
                            {'name': 'Kadaren', 'planet': '2', 'concentration':	0.171, 'gravity': 1.23, 'distanceToArrival': 26, 'type': 'rocks'},
                            {'name': 'HIP 48141', 'planet': 'C 1 A', 'concentration': 0.165, 'gravity': 0.06, 'distanceToArrival': 180, 'type': 'rocks'},
            ],
            'vanadium':   [ {'name': '102 Iota Tauri', 'planet': 'B 2 A', 'concentration': 0.109, 'gravity': 0.19, 'distanceToArrival': 3776, 'type': 'rocks'},
                            {'name': 'Nu Tauri', 'planet': '1', 'concentration':	0.109, 'gravity': 2.29, 'distanceToArrival': 828, 'type': 'rocks'},
                            {'name': 'Clota', 'planet': '1', 'concentration': 0.107, 'gravity': 1.51, 'distanceToArrival': 12, 'type': 'rocks'},
                            {'name': 'Dhakhan', 'planet': 'C 2', 'concentration': 0.105, 'gravity': 0.08, 'distanceToArrival': 13361, 'type': 'rocks'},
                            {'name': 'HIP 22286', 'planet': '2', 'concentration': 0.109, 'gravity': 1.49, 'distanceToArrival': 16, 'type': 'rocks'}
            ],
            'zinc':       [ {'name': 'LTT 6705', 'planet': 'A 2', 'concentration': 0.115, 'gravity': 0.93, 'distanceToArrival': 25, 'type': 'rocks'},
                            {'name': 'Alpha Chamaelontis', 'planet': 'B 1 A', 'concentration': 0.114, 'gravity': 0.13, 'distanceToArrival': 1786, 'type': 'rocks'},
                            {'name': 'Epsilon Ceti', 'planet': 'A 1', 'concentration':	0.113, 'gravity': 1.92, 'distanceToArrival': 85, 'type': 'rocks'},
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
        copy(best["name"])
        if best.get("type", None) is 'crystals':
            return [
                _(u'{} ({}LY), Planet {} ({}LS, {}G), {} @ biological sites').format(best['name'], pretty_dist, best['planet'], best['distanceToArrival'], best['gravity'], resource),
                _(u"Bring: detailed surface scanner, SRV, synth materials for SRV fuel and ammo."),
                _(u"Surface scan the planet to find biological sites."),
                _(u"Land, deploy SRV to break crystalline shards, scoop grade 4 materials.")
            ]            
        else:
            return [
                _(u'{} ({}LY), Planet {} ({}LS, {}G), {} @ {}%').format(best['name'], pretty_dist, best['planet'], best['distanceToArrival'], best['gravity'], resource, int(100*best['concentration'])),
                _(u"Bring: advanced scanner, SRV."),
                _(u"Break some rocks. Higher chances of Very Rare and Rare resources in metallic meteorite, metallic outcrop and mesosiderite.")
            ]

    def recommend_raw_depletable(self, resource, reference_system, callback):
        depletables = EDRRawDepletables()
        candidates = depletables.hotspots(resource)
        if not candidates:
            return False

        best_distance = None
        best = None
        for hotspot in candidates:
            distance = self.edr_systems.distance(reference_system, hotspot[0])
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best = hotspot
        
        pretty_dist = _(u"{distance:.3g}").format(distance=best_distance) if best_distance < 50.0 else _(u"{distance}").format(distance=int(best_distance))
        copy(best[0])
        return [
            _(u'{} ({}LY), Planet {} ({}LS, {}G), {}').format(best[0], pretty_dist, best[1], best[3], best[2], best[4]),
            _(u"Bring: SRV, synth materials for SRV fuel and ammo."),
            _(u"Get within 500LS of the planet to find the tourist spot."),
            _(u"Land, deploy SRV to break the crystals, and scoop high grade materials.")
        ]

    def recommend_prospecting_ring(self, resource, reference_system, callback):
        rings_lut = {
            'painite': [
                { 'system': 'HR 6844', 'ring': 'A 3 ring A', 'distanceToRing': 1196, 'tuple': 2, 'by': 'GramNam'},
                { 'system': 'HIP 76772', 'ring': '2 ring A', 'distanceToRing': 1696, 'tuple': 2, 'by': 'Boc Soma'},
                { 'system': 'HIP 73269', 'ring': 'A 1 ring A', 'distanceToRing': 2156, 'tuple': 2, 'by': 'Flemming'},
                { 'system': 'HIP 80266', 'ring': '6 ring A', 'distanceToRing': 2978, 'tuple': 2, 'by': 'Kaostic'},
                { 'system': 'HIP 19054', 'ring': '1 ring A', 'distanceToRing': 1713, 'tuple': 2, 'by': 'Ace Rimmer'},
                { 'system': 'Eol Prou QX-T d3-415', 'ring': '4 ring A', 'distanceToRing': 3127, 'tuple': 1, 'by': 'Derek Poulter'},
                { 'system': 'Eol Prou PH-K c9-497', 'ring': 'A3 ring A', 'distanceToRing': 2043, 'tuple': 1, 'by': 'Derek Poulter'},
                { 'system': 'Eol Prou RS-T d3-660', 'ring': 'ABC3 ring A', 'distanceToRing': 5948, 'tuple': 2, 'by': 'Fuchsov'},
                { 'system': 'Eol Prou PC-K c9-104', 'ring': '3 ring A', 'distanceToRing': 3027, 'tuple': 2, 'by': 'Fuchsov'},
                { 'system': 'Eol Prou HQ-N c7-13', 'ring': '4 ring A', 'distanceToRing': 390, 'tuple': 2, 'by': 'Kit Carter'},
                { 'system': 'Randgnid', 'ring': '4 ring A', 'distanceToRing': 468, 'tuple': 2, 'by': 'Schmictic'},
                { 'system': 'Hyades Sector DB-X d1-112', 'ring': '2 ring A', 'distanceToRing': 2396, 'tuple': 2, 'by': None},
                { 'system': 'Omicron Capricorni B', 'ring': 'B1 ring A', 'distanceToRing': 11524, 'tuple': 2, 'by': None},
                { 'system': 'HIP 21991', '1 ring A': '4 ring A', 'distanceToRing': 1184, 'tuple': 2, 'by': None},
                { 'system': 'HIP 59425', '2 ring A': '4 ring A', 'distanceToRing': 1787, 'tuple': 2, 'by': None},
                { 'system': 'HIP 66481', 'ring': '8 ring A', 'distanceToRing': 1350, 'tuple': 2, 'by': None},
                { 'system': 'HIP 25368', 'ring': '1 ring A', 'distanceToRing': 53, 'tuple': 2, 'by': None},
                { 'system': 'Xi-2 Lupi', 'ring': 'A2 ring A', 'distanceToRing': 1426, 'tuple': 2, 'by': None},
                { 'system': 'HIP 37222', 'ring': '3 ring A', 'distanceToRing': 2019, 'tuple': 2, 'by': None}
            ],
            'low temperature diamonds': [
                {'system':'Borann', 'ring':'A2 ring B', 'distanceToRing': 902, 'tuple': 3, 'by': 'haltingpoint'},
                {'system':'Tjupali', 'ring':'8 ring A', 'distanceToRing': 1448, 'tuple': 2, 'by': None},
                {'system':'HIP 7799', 'ring':'BCD7 ring A', 'distanceToRing': 101999, 'tuple': 2, 'by': None},
                {'system':'HIP 39383', 'ring':'BC7 ring B', 'distanceToRing': 384698, 'tuple': 2, 'by': None},
                {'system':'Arietis Sector FG-X b1-5', 'ring':'8 ring B', 'distanceToRing': 943, 'tuple': 2, 'by': None},
                {'system':'Col 285 Sector SU-F c11-19', 'ring':'ABC1 ring A', 'distanceToRing': 3143, 'tuple': 2, 'by': 'ElectricNacho'},
                {'system':'Hyades Sector SD-T c3-4', 'ring':'4 ring B', 'distanceToRing': 736, 'tuple': 2, 'by': None},
                {'system':'Bokomu', 'ring':'2 ring B', 'distanceToRing': 1664, 'tuple': 2, 'by': None},
                {'system':'Pleiades Sector VZ-O b6-3', 'ring':'9 ring A', 'distanceToRing': 1414, 'tuple': 2, 'by': None},
                {'system':'Lagoon Sector BW-M b7-2', 'ring':'A5 ring A', 'distanceToRing': 1948, 'tuple': 3, 'by': 'thicky_kemp'},
                {'system':'Eol Prou HG-M c8-9', 'ring':'BC3 ring A', 'distanceToRing': 29911, 'tuple': 3, 'by': None},
                {'system':'Coeus', 'ring':'A2 ring B', 'distanceToRing': 1590, 'tuple': 2, 'by': None},
            ],
            'bromellite': [
                { 'system': 'Irusan', 'ring': '3 ring B', 'distanceToRing': 1715, 'tuple': 3, 'by': 'SpanningTheBlack & BeornK'},
                { 'system': 'Ngorowai', 'ring': ' A 15 ring A', 'distanceToRing': 2315, 'tuple': 2, 'by': 'Merganser'},
                { 'system': 'Lyncis Sector AV-Y c8', 'ring': '3 ring A', 'distanceToRing': 21713, 'tuple': 2, 'by': 'AnubisNor'},
                { 'system': 'Pleiades Sector VZ-O b6-3', 'ring': '8 ring B', 'distanceToRing': 1078, 'tuple': 2, 'by': 'Norrwin'}, 
            ]
        }

        candidates = rings_lut.get(resource, None)
        if not candidates:
            return False

        best_distance = None
        best = None
        for ring in candidates:
            distance = self.edr_systems.distance(reference_system, ring['system'])
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best = ring
        
        pretty_dist = _(u"{distance:.3g}").format(distance=best_distance) if best_distance < 50.0 else _(u"{distance}").format(distance=int(best_distance))
        copy(best["system"])

        resource_grade = _(u"{}{}").format(resource, u"+"*best['tuple'])
        by_line = _(u"by Cmdr {}").format(best['by']) if best['by'] else u""
        return [
                _(u'{sys} ({sdist}LY), {body} ({bdist}LS): {grade} {by}').format(sys=best['system'], sdist=pretty_dist, body=best['ring'], bdist=best['distanceToRing'], grade=resource_grade, by=by_line),
                _(u"Bring: detailed surface scanner, prospector & collector limpets, mining lasers."),
                _(u"Scan the ring to find overlapping {} hotspots.").format(resource),
                _(u"Drop in there, prospect asteroids, mine the ones with {}, collect, repeat.").format(resource)
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

        copy(poi['name'])
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

    def assess_jump(self, fsdjump_event, inventory):
        if not "Factions" in fsdjump_event:
            return None
        security = fsdjump_event.get('SystemSecurity', '')
        population = fsdjump_event.get('Population', 0)
        factions = fsdjump_event.get('Factions', [])
        self.edr_factions.process(factions, fsdjump_event["StarSystem"])
        return self.edr_factions.summarize_yields(fsdjump_event["StarSystem"], security, population, inventory)
        
    def assess_signal(self, fsssignal_event, location, inventory):
        uss_type = fsssignal_event.get("USSType", None)    
        state = EDRFaction._simplified_state(fsssignal_event.get("SpawningState", None))
        faction = self.edr_factions.get(fsssignal_event.get("SpawningFaction", ""), location.star_system)
        if faction is None:
            faction = EDRFaction({"Name": fsssignal_event.get("SpawningFaction", None), "FactionState": state })            
        security = location.security
        population = location.population
        if uss_type == "$USS_Type_VeryValuableSalvage;":        
            return faction.hge_yield(security, population, state, inventory)
        elif uss_type == "$USS_Type_ValuableSalvage;":
            return faction.ee_yield(security, population, state, inventory)
        return None


    @staticmethod
    def assess_materials_density(materials_density, inventory):
        if not materials_density:
            return None
        noteworthy = []
        for material in materials_density:
            name = material["Name"]
            if name not in EDRResourceFinder.RAW_MATS:
                continue
            reference = EDRResourceFinder.RAW_MATS[name]
            if "typical" not in reference or "highest" not in reference:
                continue
            if material["Percent"] <= reference["typical"]:
                continue

            grade = (material["Percent"] - reference["typical"]) / (reference["highest"] - reference["typical"])
            chance = '+' * int(min(5, round(abs(grade)*5, 0)))
            oneliner = inventory.oneliner(name)
            noteworthy.append(_(u"{raw} {chance} @ {actual:.1f}% (median={typical:.1f}%; max={max:.1f}%)").format(raw=oneliner, chance=chance, actual=material["Percent"], typical=reference["typical"], max=reference["highest"]))
        return noteworthy