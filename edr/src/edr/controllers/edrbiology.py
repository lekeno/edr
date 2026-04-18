import json
from edr.utils.edrpath import edr_data_path
from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _, _c

class EDRBiology:
    BIOLOGY = json.loads(open(edr_data_path('biology.json')).read())

    def __init__(self, edrsystems):
        self.edrsystems = edrsystems

    @staticmethod
    def planet_walkable(planet):
        landable = planet.get("isLandable", False)
        # Walkable: landable, temp < 800K, gravity < 2.7G, pressure < 0.1 atm (if present)
        # Note: the original code had a bug or specific logic where it checked for pressure if present but defaulted to True if not?
        # Let's stick to the original logic:
        walkable = planet.get("surfaceTemperature", 1000) < 800 and planet.get("gravity", 3) < 2.7 and (not planet.get("surfacePressure") or planet.get("surfacePressure", 0) < 0.1)
        return landable and walkable

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

    @staticmethod
    def meets_biome_conditions(planet):
        if not EDRBiology.planet_walkable(planet):
            return False
        
        if planet.get("mapped", False) and not planet.get("genuses"):
            # SAA scan complete but no bio signals
            return False
        
        atmosphere = EDRBiology.canonical_atmosphere(planet)
        if atmosphere not in ["water", "waterrich", "helium", "neon", "neonrich", "argon", "argonrich", "methane", "methanerich", "nitrogen", "oxygen", "ammonia", "carbondioxide", "carbondioxiderich", "sulphurdioxide"]:
            return False
        
        planet_class = EDRBiology.canonical_planet_class(planet)
        if atmosphere == "sulphurdioxide":
            return planet_class in ["highmetalcontent", "icy", "rockyice", "rocky"]
        
        if atmosphere in ["carbondioxide", "carbondioxiderich"]:
            return planet_class in ["highmetalcontent", "rocky"]

        if atmosphere == "ammonia":
            return planet_class in ["highmetalcontent", "rocky"]
        
        return True

    def expected_bio_on_planet(self, planet, system_name):
        if planet.get("mapped", False) and not planet.get("genuses"):
            # skip SAA complete scanned with no bio signals
            return {}
        
        EDR_LOG.info("Expected bio on planet {} in system {}".format(planet.get("name", "???"), system_name))
        credits = {}
        species = []
        detected_genuses = planet.get("genuses")
        genuses_present = []
        EDR_LOG.info("Detected genuses: {}".format(detected_genuses))
        atmosphere = self.canonical_atmosphere(planet)
        planet_class = self.canonical_planet_class(planet)
        volcanism = planet.get("volcanismType", "").lower()
        gravity = planet.get("gravity", 0) # Already normalized in some contexts? Assuming raw for now.
        mean_temperature = planet.get("surfaceTemperature", 1000)
        
        # Call back to edrsystems for stellar info
        star_type = self.edrsystems.parent_star_type(system_name, planet)
        luminosity = self.edrsystems.parent_star_luminosity(system_name, planet)
        distance_from_parent_star = self.edrsystems.parent_star_distance(system_name, planet)

        if atmosphere == "noatmosphere":
            if star_type == "A" and planet_class == "metalrich":
                self.__maybe_append(species, genuses_present, _("Amphora(?)"), "amphora", detected_genuses)
            
            if star_type in ["O", "B"]:
                self.__maybe_append(species, genuses_present, _("Anemones"), "anemone", detected_genuses)
                
            if star_type == "A":
                self.__maybe_append(species, genuses_present, _("Anemones(?)"), "anemone", detected_genuses)

            if star_type in ["A", "F", "G", "K", "M", "S"]:
                if mean_temperature < 273 and distance_from_parent_star > 12000:
                    conditions = set(["earthlike", "ammonia", "gasgiantwithwaterbasedlife", "gasgiantwithammoniabasedlife", "watergiant"])
                    if self.edrsystems.has_planet_type(system_name, conditions):
                        self.__maybe_append(species, genuses_present, _("Crystalline shard"), "crystalline shard", detected_genuses)

            self.__add_missing_genuses(species, genuses_present, detected_genuses)
            return {
                "species": species,
                "genuses": genuses_present,
                "credits": credits
            }
        
        if not self.planet_walkable(planet):
            EDR_LOG.info("High gravity or not landable => no bio expected")
            self.__add_missing_genuses(species, genuses_present, detected_genuses)
            return {
                "species": species,
                "genuses": genuses_present,
                "credits": credits
            }

        # The massive if/elif block for atmospheres goes here.
        # I'll use a slightly more compact style or just move the rest in a second chunk if needed.
        # But for now, let's target the main ones.
        return self.__expected_bio_on_atmo_planet(planet, system_name, atmosphere, planet_class, volcanism, star_type, luminosity, distance_from_parent_star, detected_genuses, species, genuses_present, credits, gravity, mean_temperature)

    def __expected_bio_on_atmo_planet(self, planet, system_name, atmosphere, planet_class, volcanism, star_type, luminosity, distance_from_parent_star, detected_genuses, species, genuses_present, credits, gravity, mean_temperature):
        if atmosphere in ["water", "waterrich"]:
            bacterium = _("Bacterium Cerbrus")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses, ["$codex_ent_bacterial_12_name;"], credits)
            self.__maybe_append(species, genuses_present, _("Concha Renibus"), "Conchas", detected_genuses, ["$codex_ent_conchas_01_name;"], credits)
            fungoidas = _("Fungoida Gelata") + "/" + _("Stabitis")
            self.__maybe_append(species, genuses_present, fungoidas, "Fungoids", detected_genuses, ["$codex_ent_fungoids_02_name;", "$codex_ent_fungoids_04_name;"], credits)
            self.__maybe_append(species, genuses_present, _("Cactoida Vermis"), "Cactoids", detected_genuses, ["$codex_ent_cactoid_03_name;"], credits)

            if mean_temperature >= 165:
                if planet_class == "rocky":
                    self.__maybe_append(species, genuses_present, _("Stratum Paleas"), "Stratum", detected_genuses, ["$codex_ent_stratum_02_name;"], credits)
                else:
                    self.__maybe_append(species, genuses_present, _("Stratum Tectonicas"), "Stratum", detected_genuses, ["$codex_ent_stratum_07_name;"], credits)

            if mean_temperature >= 190:
                clypeus = _("Clypeus Lacrimam") + "/" + _("Margaritus")
                int_names = ["$codex_ent_clypeus_01_name;", "$codex_ent_clypeus_02_name;"]
                if distance_from_parent_star > 2500:
                    clypeus += "/" + _("Speculumi")
                    int_names.append("$codex_ent_clypeus_03_name;")
                self.__maybe_append(species, genuses_present, clypeus, "Clypeus", detected_genuses, int_names, credits)

            if planet_class == "rocky":
                self.__maybe_append(species, genuses_present, _("Frutexa Sponsae"), "Shrubs", detected_genuses, ["$codex_ent_shrubs_06_name;"], credits)
                self.__maybe_append(species, genuses_present, _("Osseus Discus"), "Osseus", detected_genuses, ["$codex_ent_osseus_02_name;"], credits)
                self.__maybe_append(species, genuses_present, _("Tussock Virgam"), "tussocks", detected_genuses, ["$codex_ent_tussocks_14_name;"], credits)
            elif planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses_present, _("Fumerola Aquatis"), "Fumerolas", detected_genuses, ["$codex_ent_fumerolas_04_name;"], credits)
            elif planet_class == "highmetalcontent":
                self.__maybe_append(species, genuses_present, _("Osseus Discus"), "Osseus", detected_genuses, ["$codex_ent_osseus_02_name;"], credits)
                self.__maybe_append(species, genuses_present, _("Tussock Virgam"), "tussocks", detected_genuses, ["$codex_ent_tussocks_14_name;"], credits)
        
        elif atmosphere == "helium":
            bacterium = _("Bacterium Nebulus")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            if self.edrsystems.near_nebula(system_name):
                self.__maybe_append(species, genuses_present, _("Electricae Radialem"), "Electricae", detected_genuses)
            elif (star_type == "A" and luminosity.startswith("V")) or star_type in ["White Dwarf (DA)", "DA"]:
                self.__maybe_append(species, genuses_present, _("Electricae Pluma"), "Electricae", detected_genuses)

        elif atmosphere in ["neon", "neonrich"]:
            self.__maybe_append(species, genuses_present, _("Fonticulua segmentatus"), "Fonticulus", detected_genuses)
            bacterium = _("Bacterium Acies")
            if volcanism == "water":
                bacterium += "/" + _("Verrata")
            elif volcanism in ["nitrogen", "ammonia"]:
                bacterium += "/" + _("Omentum")
            elif volcanism in ["carbon", "methane"]:
                bacterium += "/" + _("Scopulum")
            elif volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)

            if self.edrsystems.near_nebula(system_name):
                self.__maybe_append(species, genuses_present, _("Electricae Radialem"), "Electricae", detected_genuses)
            elif (star_type == "A" and luminosity.startswith("V")) or star_type in ["White Dwarf (DA)", "DA"]:
                self.__maybe_append(species, genuses_present, _("Electricae Pluma"), "Electricae", detected_genuses)

        elif atmosphere in ["argon", "argonrich"]:
            bacterium = _("Bacterium Vesicula")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Fungoida Bullarum"), "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Osseus Pumice"), "Osseus", detected_genuses)
            if planet_class == "rocky":
                self.__maybe_append(species, genuses_present, _("Tussock Capillum"), "tussocks", detected_genuses)
            if atmosphere == "argon" and planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses_present, _("Fonticulua Campestris"), "Fonticulus", detected_genuses)
            elif atmosphere == "argonrich" and planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses_present, _("Fonticulua Upupam"), "Fonticulus", detected_genuses)
            if self.edrsystems.near_nebula(system_name):
                self.__maybe_append(species, genuses_present, _("Electricae Radialem"), "Electricae", detected_genuses)
            elif (star_type == "A" and luminosity.startswith("V")) or star_type in ["White Dwarf (DA)", "DA"]:
                self.__maybe_append(species, genuses_present, _("Electricae Pluma"), "Electricae", detected_genuses)
        elif atmosphere in ["methane", "methanerich"]:
            self.__maybe_append(species, genuses_present, _("Fungoida Setisis"), "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Osseus Pumice"), "Osseus", detected_genuses)
            bacterium = _("Bacterium Bullaris")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            if planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses_present, _("Fonticulua Digitos"), "Fonticulus", detected_genuses)
            elif planet_class == "rocky":
                self.__maybe_append(species, genuses_present, _("Tussock Capillum"), "tussocks", detected_genuses)
        elif atmosphere == "nitrogen":
            self.__maybe_append(species, genuses_present, _("Concha Biconcavis"), "Conchas", detected_genuses)
            bacterium = _("Bacterium Informem")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            if planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses_present, _("Fonticulua Lapida"), "Fonticulus", detected_genuses)
        elif atmosphere == "oxygen":
            bacterium = _("Bacterium Volu")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            if planet_class in ["icy", "rockyice"]:
                self.__maybe_append(species, genuses_present, _("Fonticulua Fluctus"), "Fonticulus", detected_genuses)
            elif planet_class == "highmetalcontent" and mean_temperature > 165:
                self.__maybe_append(species, genuses_present, _("Stratum Tectonicas"), "Stratum", detected_genuses)
        elif atmosphere == "ammonia" and planet_class == "rocky":
            aleoidas = _("Aleoida Laminiae") + "/" + _("Spica")
            self.__maybe_append(species, genuses_present, aleoidas, "Aleoids", detected_genuses)
            cactoidas = _("Cactoida Lapis") + "/" + _("Peperatis")
            self.__maybe_append(species, genuses_present, cactoidas, "Cactoids", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Concha Aureolas"), "Conchas", detected_genuses)
            shrubs = _("Frutexa Flabellum") + "/" + _("Flammasis")
            self.__maybe_append(species, genuses_present, shrubs, "shrubs", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Fungoida Setisis"), "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Osseus Spiralis"), "Osseus", detected_genuses)
            tussocks = _("Tussock Catena") + "/" + _("Cultro") + "/" + _("Divisa")
            self.__maybe_append(species, genuses_present, tussocks, "Tussocks", detected_genuses)
            bacterium = _("Bacterium Alcyoneum")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            if gravity < 0.15:
                self.__maybe_append(species, genuses_present, _("Tubus Rosarium"), "Tubus", detected_genuses)
            if mean_temperature > 165:
                stratums = _("Stratum Paleas") + "/" + _("Laminamus")
                self.__maybe_append(species, genuses_present, stratums, "Stratum", detected_genuses)
        elif atmosphere == "ammonia" and planet_class == "highmetalcontent":
            bacterium = _("Bacterium Alcyoneum")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            aleoidas = _("Aleoida Laminiae") + "/" + _("Spica")
            self.__maybe_append(species, genuses_present, aleoidas, "Aleoids", detected_genuses)
            cactoidas = _("Cactoida Lapis") + "/" + _("Peperatis")
            self.__maybe_append(species, genuses_present, cactoidas, "Cactoids", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Concha Aureolas"), "Conchas", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Frutexa Metallicum"), "Shrubs", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Fungoida Setisis"), "Fungoids", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Osseus Spiralis"), "Osseus", detected_genuses)
            if gravity < 0.15:
                self.__maybe_append(species, genuses_present, _("Tubus Sororibus"), "Tubus", detected_genuses)
            if mean_temperature > 165:
                self.__maybe_append(species, genuses_present, _("Stratum Tectonicas"), "Stratum", detected_genuses)
        elif atmosphere in ["carbondioxide", "carbondioxiderich"] and planet_class == "rocky":
            bacterium = _("Bacterium Aurasus")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            conchas = _("Concha Labiata")
            shrubs = _("Frutexa Acus") + "/" + _("Fera")
            self.__maybe_append(species, genuses_present, shrubs, "shrubs", detected_genuses)
            tussocks = _("Tussock Propagito") + "/" + _("Pennatis")
            if 145 < mean_temperature < 155:
                tussocks += "/" + _("Pennata")
            elif 155 < mean_temperature < 160:
                tussocks += "/" + _("Ventusa")
            elif 160 < mean_temperature < 170:
                tussocks += "/" + _("Ignis")
            elif 170 < mean_temperature < 175:
                tussocks += "/" + _("Serrati")
            elif 175 < mean_temperature < 180:
                tussocks += "/" + _("Albata")
                self.__maybe_append(species, genuses_present, _("Aleoida Arcus"), "Aleoids", detected_genuses)
            elif 180 < mean_temperature < 190:
                self.__maybe_append(species, genuses_present, _("Aleoida Coronamus"), "Aleoids", detected_genuses)
                cactoidas = _("Cactoida Cortexum") + "/" + _("Pullulanta")
                self.__maybe_append(species, genuses_present, cactoidas, "cactoids", detected_genuses)
                conchas += "/" + _("Renibus")
                osseuses = _("Osseus Fractus") + "/" + _("Cornibus")
                self.__maybe_append(species, genuses_present, osseuses, "osseus", detected_genuses)
                tussocks += "/" + _("Caputus")
                fungoidas = _("Fungoida Gelata") + "/" + _("Stabitis")
                self.__maybe_append(species, genuses_present, fungoidas, "Fungoids", detected_genuses)
            elif 180 < mean_temperature < 195:
                cactoidas = _("Cactoida Cortexum") + "/" + _("Pullulanta")
                self.__maybe_append(species, genuses_present, cactoidas, "cactoids", detected_genuses)
                conchas += "/" + "Renibus"
                self.__maybe_append(species, genuses_present, _("Osseus Cornibus"), "Osseus", detected_genuses)
                tussocks += "/" + _("Caputus")
                fungoidas = _("Fungoida Gelata") + "/" + _("Stabitis")
                self.__maybe_append(species, genuses_present, fungoidas, "Fungoids", detected_genuses)
            
            if 160 < mean_temperature < 190 and gravity < 0.15:
                tubus = _("Tubus Cavas") + "/" + _("Compagibus") + "/" + _("Conifer")
                self.__maybe_append(species, genuses_present, tubus, "tubus", detected_genuses)
            
            if mean_temperature > 190:
                clypeuses = _("Clypeus Lacrimam") + "/" + _("Margaritus")
                if distance_from_parent_star > 2500:
                    clypeuses += "/" + _("Speculumi")
                self.__maybe_append(species, genuses_present, clypeuses, "clypeus", detected_genuses)

                if mean_temperature < 195:
                    self.__maybe_append(species, genuses_present, _("Aleoida Gravis"), "Aleoids", detected_genuses)
                    self.__maybe_append(species, genuses_present, _("Osseus Pellebantus"), "Osseus", detected_genuses)
                    tussocks += "/" + _("Triticum")
            
            if mean_temperature > 165:
                stratums = _("Stratum Paleas")
                if  mean_temperature < 190:
                    stratums += "/" + _("Excutitus")
                else:
                    stratums += "/" + _("Limaxus") + "/" + _("Frigus") + "/" + _("Cucumisis")
                self.__maybe_append(species, genuses_present, stratums, "stratum", detected_genuses)

            self.__maybe_append(species, genuses_present, tussocks, "tussocks", detected_genuses)
            self.__maybe_append(species, genuses_present, conchas, "conchas", detected_genuses)
        elif atmosphere in ["carbondioxide", "carbondioxiderich"] and planet_class == "highmetalcontent":
            bacterium = _("Bacterium Aurasus")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Frutexa Metallicum"), "Shrubs", detected_genuses)
            if 175 < mean_temperature < 180:
                self.__maybe_append(species, genuses_present, _("Aleoida Arcus"), "Aleoids", detected_genuses)
            elif 180 < mean_temperature < 190:
                self.__maybe_append(species, genuses_present, _("Aleoida Coronamus"), "Aleoids", detected_genuses)
            elif 190 < mean_temperature < 195:
                self.__maybe_append(species, genuses_present, _("Aleoida Gravis"), "Aleoids", detected_genuses)
            
            if 180 < mean_temperature < 195:
                cactoidas = _("Cactoida Cortexum") + "/" + _("Pullulanta")
                self.__maybe_append(species, genuses_present, cactoidas, "Cactoids", detected_genuses)                
            
            conchas = None
            if 180 < mean_temperature < 195:
                conchas = _("Concha Renibus")
                fungoidas = _("Fungoida Gelata") + "/" + _("Stabitis")
                self.__maybe_append(species, genuses_present, fungoidas, "fungoids", detected_genuses)

            if mean_temperature < 190:
                if conchas:
                    conchas += "/" + _("Labiata")
                else:
                    conchas = _("Concha Labiata")
            if conchas:
                self.__maybe_append(species, genuses_present, conchas, "conchas", detected_genuses)

            osseuses = None
            if mean_temperature > 180:
                if mean_temperature < 195:
                    osseuses = _("Osseus Cornibus")
                    if mean_temperature > 190:
                        osseuses += "/" + _("Pellebantus")
                if mean_temperature < 190:
                    if not osseuses:
                        osseuses = _("Osseus Fractus")
                    else:
                        osseuses += "/" + _("Fractus")
            if osseuses:
                self.__maybe_append(species, genuses_present, osseuses, "osseus", detected_genuses)
            
            if 160 < mean_temperature < 190 and gravity < 0.15:
                self.__maybe_append(species, genuses_present, _("Tubus Sororibus"), "tubus", detected_genuses)

            if mean_temperature > 190:
                clypeuses = _("Clypeus Lacrimam") + "/" + _("Margaritus")
                if distance_from_parent_star > 2500:
                    clypeuses += "/" + _("Speculumi")
                self.__maybe_append(species, genuses_present, clypeuses, "clypeus", detected_genuses)
            
            if mean_temperature > 165:
                self.__maybe_append(species, genuses_present, _("Stratum Tectonicas"), "stratum", detected_genuses)
        elif atmosphere == "sulphurdioxide" and planet_class in ["icy", "rockyice"]:
            receptas = _("Recepta Umbrux") + "/" + _("Conditivus")
            self.__maybe_append(species, genuses_present, receptas, "Recepta", detected_genuses)
            bacterium = _("Bacterium Cerbrus")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
        elif atmosphere == "sulphurdioxide" and planet_class == "rocky":
            self.__maybe_append(species, genuses_present, _("Frutexa Collum"), "Shrubs", detected_genuses)
            receptas = _("Recepta Deltahedronix") + "/" + _("Umbrux")
            self.__maybe_append(species, genuses_present, receptas, "Recepta", detected_genuses)
            self.__maybe_append(species, genuses_present, _("Tussock Stigmasis"), "tussocks", detected_genuses)
            bacterium = _("Bacterium Cerbrus")
            stratums = None
            if mean_temperature > 165:
                stratums = _("Stratum Araneamus")
                if mean_temperature < 190:
                    stratums += "/" + _("Excutitus") + "/" + _("Limaxus")
                else:
                    stratums += "/" + _("Frigus") + "/" + _("Cucumisis")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            if stratums:
                self.__maybe_append(species, genuses_present, stratums, "Stratum", detected_genuses)
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
        elif atmosphere == "sulphurdioxide" and planet_class == "highmetalcontent":
            receptas = _("Recepta Deltahedronix") + "/" + _("Umbrux")
            self.__maybe_append(species, genuses_present, receptas, "Recepta", detected_genuses)
            bacterium = _("Bacterium Cerbrus")
            if volcanism in ["helium", "iron", "silicate"]:
                bacterium += "/" + _("Tela")
            self.__maybe_append(species, genuses_present, bacterium, "Bacterium", detected_genuses)
            if mean_temperature > 165:
                self.__maybe_append(species, genuses_present, _("Stratum Tectonicas"), "Stratum", detected_genuses)

        self.__add_missing_genuses(species, genuses_present, detected_genuses)
        return {
            "species": species,
            "genuses": genuses_present,
            "credits": credits
        }

    def __maybe_append(self, biome, genuses, species, genus, detected_genuses, int_species_names=None, credits=None):
        if detected_genuses is not None and len(detected_genuses) == 0:
            return

        CGENUS_LUT = self.BIOLOGY.get("genuses_int_names", {})
        cgenus = CGENUS_LUT.get(genus.lower(), "unknown")
        if cgenus not in genuses:
            genuses.append(cgenus)

        species_added = False
        if not detected_genuses:
            biome.append(species)
            species_added = True
        elif cgenus == "unknown":
            EDR_LOG.warning("Unknown genus: {}".format(genus))
            biome.append(species)
            species_added = True
        else:
            for g in detected_genuses:
                if cgenus in g["Genus"]:
                    biome.append(species)
                    species_added = True
                    break

        if species_added and credits and int_species_names:
            for int_name in int_species_names:
                credit = self.__bio_credits(int_name)
                if cgenus not in credits:
                    credits[cgenus] = {"min": credit, "max": credit}
                else:
                    credits[cgenus] = {
                        "min": min(credit, credits[cgenus]["min"]),
                        "max": max(credit, credits[cgenus]["max"])
                    }

    def __bio_credits(self, a_species_int_name):
        cname = a_species_int_name.lower()
        if cname not in self.BIOLOGY["species"]:
            return 0
        return self.BIOLOGY["species"][cname]["credits"]

    def __add_missing_genuses(self, biome, genuses, detected_genuses):
        if detected_genuses is None or len(detected_genuses) == 0:
            return
        
        GENUS_LUT = {
            "$Codex_Ent_Aleoids_Genus_Name;": _("Aleoids"),
            "$Codex_Ent_Sphere_Genus_Name;": _("Anemone"),
            "$Codex_Ent_Bacterial_Genus_Name;": _("Bacterium"),
            "$Codex_Ent_Cone_Genus_Name;": _("Bark mound"),
            "$Codex_Ent_Seed_Genus_Name;": _("Seed"),
            "$Codex_Ent_Cactoid_Genus_Name;": _("Cactoids"),
            "$Codex_Ent_Clypeus_Genus_Name;": _("Clypeus"),
            "$Codex_Ent_Conchas_Genus_Name;": _("Conchas"),
            "$Codex_Ent_Electricae_Genus_Name;": _("Electricae"),
            "$Codex_Ent_Fonticulus_Genus_Name;": _("Fonticulus"),
            "$Codex_Ent_Shrubs_Genus_Name;": _("Frutexa"),
            "$Codex_Ent_Fumerolas_Genus_Name;": _("Fumerolas"),
            "$Codex_Ent_Fungoids_Genus_Name;": _("Fungoids"),
            "$Codex_Ent_Osseus_Genus_Name;": _("Osseus"),
            "$Codex_Ent_Recepta_Genus_Name;": _("Recepta"),
            "$Codex_Ent_Tube_Genus_Name;": _("Sinuous tuber"),
            "$Codex_Ent_Stratum_Genus_Name;": _("Stratum"),
            "$Codex_Ent_Tubus_Genus_Name;": _("Tubus"),
            "$Codex_Ent_Tussocks_Genus_Name;": _("Tussocks"),
            "$Codex_Ent_Ground_Struct_Ice_Name;": _("Crystalline shards"),
            "$Codex_Ent_Vents_Name;": _("Amphora")
        }

        predicted = set(genuses)
        for g in detected_genuses:
            if g["Genus"] not in GENUS_LUT:
                continue
            readable_genus = GENUS_LUT[g["Genus"]]
            if g["Genus"] not in predicted:
                biome.append(readable_genus)

    def analyzed_biome(self, star_system, body_id_or_name):
        body = self.edrsystems.body(star_system, body_id_or_name)
        if not body:
            return None
        
        if not EDRBiology.meets_biome_conditions(body):
            return None
            
        return self.expected_bio_on_planet(body, star_system)

    def biology_on(self, system_name, body_name):
        body = self.edrsystems.body(system_name, body_name)
        if not body:
            return None
        return self.expected_bio_on_planet(body, system_name)

    def biology_spots(self, system_name):
        bodies = self.edrsystems.bodies(system_name)
        if not bodies:
            return None
        
        spots = []
        for body in bodies:
            if EDRBiology.meets_biome_conditions(body):
                sname = body.get("name", "")
                if sname.startswith(system_name):
                    sname = sname[len(system_name)+1:]
                spots.append(sname)
        return spots
