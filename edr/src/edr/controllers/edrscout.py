import json
import os
from edr.utils.edrpath import edr_cache_path, edr_data_path
from edr.utils.lrucache import LRUCache
from edr.core.edrlog import EDR_LOG

class EDRScout:
    EDSM_SYSTEM_VALUES_CACHE = edr_cache_path('edsm_system_values.v1.p')

    def __init__(self, edrsystems):
        self.edrsystems = edrsystems
        self.edsm_server = edrsystems.edsm_server
        self.edsm_system_values_cache = LRUCache.load(
            file_path=self.EDSM_SYSTEM_VALUES_CACHE,
            max_size=100,
            max_age_seconds=60*60*24*31
        )

    def save(self):
        if self.edsm_system_values_cache:
            self.edsm_system_values_cache.save(self.EDSM_SYSTEM_VALUES_CACHE)

    def system_value(self, system_name):
        value = self.edsm_system_values_cache.get(system_name.lower())
        if not value:
            value = self.edsm_server.system_value(system_name)
            if value:
                self.edsm_system_values_cache.set(system_name.lower(), value)
            else:
                value = {}
        
        bodies = self.edrsystems.bodies(system_name)
        if not bodies:
            bodies = [{}]

        body_values = {b["bodyName"]: b for b in value.get("valuableBodies", [])}
        for body in bodies:
            valueMax = None
            valueScanned = None
            if body.get("type", "").lower() == "star":
                valueMax = self.star_value(body)
                valueScanned = valueMax
            else:
                valueMax = self.body_value_estimate(body)
                valueScanned = self.body_value_estimate(body, False)
            
            body_name = body.get("name", None)
            if body_name and valueMax is not None:
                if body_name in body_values:
                    body_values[body_name]["valueMax"] = valueMax
                    body_values[body_name]["valueScanned"] = valueScanned
                else:
                    distance = round(body["distanceToArrival"]) if "distanceToArrival" in body else None
                    body_values[body_name] = {
                        "bodyId": body.get("bodyId", None),
                        "bodyName": body_name,
                        "distance": distance,
                        "valueMax": valueMax,
                        "valueScanned": valueScanned
                    }
        
        total_estimated_value = 0
        for bv in body_values.values():
            if bv.get("valueMax"):
                total_estimated_value += bv["valueMax"]
        
        result = value.copy()
        result.update({
            "totalValue": total_estimated_value,
            "estimatedValue": value.get("estimatedValue", total_estimated_value),
            "valuableBodies": sorted(body_values.values(), key=lambda x: x.get("valueMax", 0), reverse=True)
        })
        return result

    def body_value(self, system_name, body_name):
        the_body = self.edrsystems.body(system_name, body_name)
        if not the_body:
            return None
        
        valueMax = None
        if the_body.get("type", "").lower() == "star":
            valueMax = self.star_value(the_body)
        else:
            valueMax = self.body_value_estimate(the_body)
            
        return {
            "valueMax": valueMax,
            "distance": round(the_body.get("distanceToArrival", 0))
        }

    @staticmethod
    def star_value(the_body, bonus=True):
        stype = the_body.get("subType", "")
        mass = the_body.get("solarMasses", 0)
        first_discoverer = not the_body.get("wasDiscovered", False)
        
        if not stype:
            return None
        
        l_stype = stype.lower()
        if "white dwarf" in l_stype or l_stype in ["d", "da", "dab", "dao", "daz", "dav", "db", "dbz", "dbv", "do", "dov", "dq", "dc", "dcv", "dx"]:
            stype = "white dwarf"
        elif l_stype == "n":
            stype = "neutron star"
        elif l_stype == "h" or l_stype == "supermassiveblackhole":
            stype = "black hole"
            
        k_lut = {"black hole": 22628, "neutron star": 22628, "white dwarf": 14057}
        k = k_lut.get(stype.lower(), 1200)
        honk_bonus_value = 0
        if bonus:
            q = 0.56591828
            honk_bonus_value = max(500, (k + k * q * pow(mass, 0.2)) / 3)
            honk_bonus_value *= 2.6 if first_discoverer else 1
            
        return round((k + (mass * k / 66.25)) + honk_bonus_value)

    def body_value_estimate(self, the_body, override_mapped=True):
        stype = the_body.get("subType", "")
        mass = the_body.get("earthMasses", 0)
        terraformability = 1.0 if the_body.get("terraformingState", "") == "Terraformed" else 0.0
        first_discoverer = not the_body.get("wasDiscovered", False)
        
        mapped = override_mapped
        first_mapped = not the_body.get("wasMapped", False) if mapped else False
        efficiency_bonus = the_body.get("wasEfficient", True) if mapped else False
        
        k_lut = {
            "metal-rich body": 21790,
            "metal rich body": 21790,
            "ammonia world": 96932,
            "sudarsky class i gas giant": 1656,
            "sudarsky class ii gas giant": 9654 + terraformability * 100677,
            "class i gas giant": 1656,
            "class ii gas giant": 9654 + terraformability * 100677,
            "high metal content world": 9654 + terraformability * 100677,
            "high metal content body": 9654 + terraformability * 100677,
            "water world": 64831 + terraformability * 116295,
            "earth-like world": 64831 + terraformability * 116295,
            "earthlike body": 64831 + terraformability * 116295
        }
        
        k = 300 + terraformability * 93328
        k = k_lut.get(stype.lower(), k)
        q = 0.56591828
        mapping_multiplier = 1
        if mapped:
            if first_discoverer and first_mapped:
                mapping_multiplier = 3.699622554
            elif first_mapped:
                mapping_multiplier = 8.0956
            else:
                mapping_multiplier = 3.3333333333
                
        value = (k + k * q * pow(mass, 0.2)) * mapping_multiplier
        
        if mapped:
            if self.edrsystems.dlc_name and self.edrsystems.dlc_name.lower() == "odyssey":
                value += max(value * 0.3, 555)
            
            if efficiency_bonus:
                value *= 1.25
                
        value = max(500, value)
        if first_discoverer:
            value *= 2.6
            
        return round(value)
