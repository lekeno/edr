import re
from edr.utils import edtime
from edr.core.edrlog import EDR_LOG
from edr.utils.edrpath import edr_cache_path
from edr.utils.lrucache import LRUCache
from edr.core.edri18n import _, _c
from . import edrsysplacheck
from . import edrplanetfinder

class EDRBody:
    EDSM_BODIES_CACHE = edr_cache_path('edsm_bodies.v1.p')
    EDR_RAW_MATERIALS_CACHE = edr_cache_path('raw_materials.v1.p')

    def __init__(self, edrsystems):
        self.edrsystems = edrsystems
        self.server = edrsystems.server
        self.edsm_server = edrsystems.edsm_server
        
        from edr.core import edrconfig
        edr_config = edrconfig.EDR_CONFIG
        self.edsm_bodies_cache = LRUCache.load(
            file_path=self.EDSM_BODIES_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_bodies_max_age()
        )
        self.materials_cache = LRUCache.load(
            file_path=self.EDR_RAW_MATERIALS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.materials_max_age()
        )

    def save(self):
        self.edsm_bodies_cache.save(self.EDSM_BODIES_CACHE)
        self.materials_cache.save(self.EDR_RAW_MATERIALS_CACHE)

    def bodies(self, system_name):
        if not system_name:
            return None
        bodies = self.edsm_bodies_cache.get(system_name.lower())
        if self.edsm_bodies_cache.has_key(system_name.lower()) or bodies:
            return bodies

        bodies = self.edsm_server.bodies_in_system(system_name)
        if bodies:
            self.edsm_bodies_cache.set(system_name.lower(), bodies)
            return bodies
        return None

    def body(self, system_name, body_name):
        if not system_name or not body_name:
            return None
        bodies = self.bodies(system_name)
        if not bodies:
            return None
        for body in bodies:
            if body.get("name", "").lower() == body_name.lower():
                return body
        return None

    def __body_with_id(self, system_name, body_id):
        bodies = self.bodies(system_name)
        if not bodies:
            return None
        for body in bodies:
            if body.get("bodyId", -1) == body_id:
                return body
        return None

    def body_name_with_id(self, system_name, body_id):
        body = self.__body_with_id(system_name, body_id)
        return body.get("name", "Unknown") if body else "Unknown"

    def body_count(self, system_name):
        bodies = self.bodies(system_name)
        if not bodies:
            return 0
        if "bodyCount" in bodies[0]:
            return max(bodies[0]["bodyCount"], len(bodies))
        return len(bodies)

    def search_planet_with_genus(self, star_system, genus, callback, override_radius = 100, override_sc_distance = 100000, permits = []):
        override_sc_distance = override_sc_distance or 100000
        checker = edrsysplacheck.EDRGenusCheckerFactory.get_checker(genus, self.edrsystems, override_sc_distance)
        if checker:
            self.__search_a_planet(star_system, callback, checker, override_radius, override_sc_distance, permits, shuffle_systems=True, shuffle_planets=True, exclude_center=True)

    def __search_a_planet(self, star_system, callback, checker, override_radius = None, override_sc_distance = None, permits = [], shuffle_systems=True, shuffle_planets=True, exclude_center=False):
        sc_distance = override_sc_distance or 1500
        sc_distance = max(250, sc_distance)
        radius = override_radius if override_radius is not None and override_radius >= 0 else 50
        radius = min(100, radius)

        finder = edrplanetfinder.EDRPlanetFinder(star_system, checker, self.edrsystems, callback)
        finder.within_radius(radius)
        finder.within_supercruise_distance(sc_distance)
        finder.permits_in_possession(permits)
        finder.shuffling(shuffle_systems, shuffle_planets)
        finder.ignore_center(exclude_center)
        finder.set_dlc(self.edrsystems.dlc_name)
        finder.start()

    def reflect_scan(self, system_name, body_name, scan):
        if "belt cluster" in body_name.lower():
            return
        
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = [{}]
        
        the_body = None
        for b in bodies:
            if b.get("name", "").lower() == body_name.lower():
                the_body = b
                break
        
        new_body = the_body is None
        if new_body:
            the_body = {}
        
        kv_lut = {
            "timestamp": {"k": "updateTime", "v": lambda v: v.replace("T", " ").replace("Z", "") if v else ""},
            "BodyName": {"k": "name", "v": lambda v: v},
            "BodyID": {"k": "bodyId", "v": lambda v: v},
            "DistanceFromArrivalLS": {"k": "distanceToArrival", "v": lambda v: v},
            "StarType": {"k": "subType", "v": lambda v: v},
            "PlanetClass": {"k": "subType", "v": lambda v: v},
        }
        
        for key in scan:
            if key in kv_lut:
                new_kv = kv_lut[key]
                if new_kv:
                    the_body[new_kv["k"]] = new_kv["v"](scan.get(key))
            else:
                # Default mapping for other keys
                k = key[:1].lower() + key[1:]
                the_body[k] = scan[key]

        the_body["scanned"] = True
        if "StarType" in scan:
            the_body["type"] = "Star"
            the_body["isScoopable"] = the_body.get("subType", "") in ["O","B","A", "F", "G", "K", "M"]
            the_body["solarRadius"] = scan["Radius"]/695500000 if scan.get("Radius", None) else None
        else:
            the_body["type"] = "Planet"
            the_body["radius"] = scan["Radius"]/1000 if scan.get("Radius", None) else None
        
        if new_body:
            bodies.append(the_body)
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)

    def reflect_organic_scan(self, system_name, body_id, scan):
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = [{}]
        
        the_body = None
        for b in bodies:
            if b.get("bodyId", -1) == body_id:
                the_body = b
                break
        
        new_body = the_body is None
        if new_body:
            the_body = {}
        
        kv_lut = {
            "timestamp": {"k": "updateTime", "v": lambda v: v.replace("T", " ").replace("Z", "") if v else ""},
            "Body": {"k": "bodyId", "v": lambda v: v},
        }
        
        for key in scan:
            if key in kv_lut:
                new_kv = kv_lut[key]
                if new_kv:
                    the_body[new_kv["k"]] = new_kv["v"](scan.get(key))
            else:
                k = key[:1].lower() + key[1:]
                the_body[k] = scan[key]

        if "species" not in the_body:
            the_body["species"] = {}
        
        the_body["species"][scan["Species"]] = {"genus": scan["Genus"], "genusLocalised": scan["Genus_Localised"], "speciesLocalised": scan["Species_Localised"]}
        
        if new_body:
            bodies.append(the_body)
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)

    def body_signals_found(self, system_name, scan):
        body_name = scan.get("BodyName", None)
        if not body_name:
            return
        
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = [{}]
        
        the_body = None
        for b in bodies:
            if b.get("name", "").lower() == body_name.lower():
                the_body = b
                break
        
        new_body = the_body is None
        if new_body:
            the_body = {}
            the_body["name"] = body_name
            the_body["bodyId"] = scan.get("BodyID", -1)

        for s in scan.get("Signals", []):
            stype = s.get("Type", None)
            if stype:
                k = stype[:1].lower() + stype[1:]
                the_body[k] = s.get("Count", 0)

        if new_body:
            bodies.append(the_body)
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)

    def fss_discovery_scan_update(self, scan):
        system_name = scan["SystemName"]
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = [{}]
        
        if "bodyCount" in bodies[0]:
            bodies[0]["bodyCount"] = scan["Count"]
        else:
            bodies[0]["bodyCount"] = scan["Count"]
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)

    def saa_scan_complete(self, scan):
        system_name = scan.get("SystemName", None)
        if not system_name:
            return
            
        body_name = scan.get("BodyName", None)
        if not body_name:
            return
        
        bodies = self.bodies(system_name)
        if not bodies:
            bodies = [{}]
        
        the_body = None
        for b in bodies:
            if b.get("name", "").lower() == body_name.lower():
                the_body = b
                break
        
        new_body = the_body is None
        if new_body:
            the_body = {}
            the_body["name"] = body_name
            the_body["bodyId"] = scan.get("BodyID", -1)
            
        the_body["wasEfficient"] = scan["ProbesUsed"] <= scan.get("EfficiencyTarget", 0)
        the_body["mapped"] = True
        
        if new_body:
            bodies.append(the_body)
        
        self.edsm_bodies_cache.set(system_name.lower(), bodies)

    def describe_body(self, system_name, body_name, current_system=True):
        belt = bool(re.match(r"^(.*) \S+ (?:Belt Cluster [0-9]+)$", body_name))
        ring = body_name.endswith("Ring")
        adj_body_name = body_name
        if belt or ring:
            m = re.match(r"^(.*) \S+ (?:Belt Cluster [0-9]+|Ring)$", body_name)
            adj_body_name = m.group(1) if m else body_name

        the_body = self.body(system_name, adj_body_name)
        if not the_body:
            return None
        details = []
        body_type = the_body.get("type", "")
        if belt and "belts" in the_body:
            details.extend(self.__describe_belt(the_body, body_name))
        elif ring and "rings" in the_body:
            details.extend(self.__describe_ring(the_body, body_name))
        elif body_type == "Star":
            if current_system:
                details.extend(self.__describe_star(the_body, system_name))
            else:
                details.extend(self.edrsystems.describe_system(system_name, current_system))
        elif body_type == "Planet":
            details.extend(self.__describe_planet(the_body, system_name))
        else:
            pass

        if "updateTime" in the_body:
            updated = edtime.EDTime()
            updated.from_edsm_timestamp(the_body["updateTime"])
            details.append(_("as of {}  ").format(updated.as_local_timestamp()))
        
        return details

    def __describe_star(self, star, system_name):
        details = []
        info = ""
        stype = star.get("subType", None)
        if stype:
            info = _(u"{} star").format(stype)
        
        details.append(info)
        info = ""
        if star.get("isMainStar", False):
            info = _(u"Main star")
        elif star.get("distanceToArrival", 0) > 0:
            info = _(u"{:,.0f}ls from arrival").format(star["distanceToArrival"])
        
        if info:
            details.append(info)
        
        return details

    def describe_primary_star(self, star, system_name, current_system=True):
        details = []
        info = ""
        stype = star.get("type", None)
        if stype:
            info = _(u"{} star").format(stype)
        
        details.append(info)
        
        if not current_system:
            info = self.edrsystems.describe_system(system_name, current_system)
            if info:
                details.extend(info)
        
        return details

    def __describe_planet(self, planet, system_name):
        details = []
        info = ""
        body_type = planet.get("type", None)
        if body_type == "Planet":
            planet_class = planet.get("subType", "Unknown")
            info = _(u"{} planet").format(planet_class)
        
        details.append(info)
        
        info = ""
        if planet.get("distanceToArrival", 0) > 0:
            info = _(u"{:,.0f}ls from arrival").format(planet["distanceToArrival"])
        
        if info:
            details.append(info)
        
        return details

    def __describe_belt(self, body, belt_full_name):
        details = []
        for belt in body.get("belts", []):
            if belt.get("name", "") == belt_full_name:
                details.append(_(u"Belt: {}").format(belt.get("type", "Unknown")))
                break
        return details

    def __describe_ring(self, body, ring_full_name):
        details = []
        for ring in body.get("rings", []):
            if ring.get("name", "") == ring_full_name:
                details.append(_(u"Ring: {}").format(ring.get("type", "Unknown")))
                break
        return details

    @staticmethod
    def canonical_planet_class(planet):
        planet_class = planet.get("subType", "Unknown").lower()
        planet_class = planet_class.replace("world", "")
        planet_class = planet_class.replace("body", "")
        planet_class = planet_class.replace(" ", "")
        planet_class = planet_class.replace("-", "")
        return planet_class

    @staticmethod
    def canonical_atmosphere(planet):
        if not planet:
            return "Unknown"
        atmosphere = planet.get("atmosphereType", "No atmosphere")
        if not atmosphere:
            return "Unknown"
        
        if atmosphere.lower().startswith("thin "):
            atmosphere = atmosphere[len("thin "):]
        atmosphere = atmosphere.replace(" ", "")
        atmosphere = atmosphere.replace("-", "")
        atmosphere = atmosphere.lower()
        return atmosphere
