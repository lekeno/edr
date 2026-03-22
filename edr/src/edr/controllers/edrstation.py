from edr.utils.edrpath import edr_cache_path
from edr.utils.lrucache import LRUCache
from edr.core import edrconfig
from edr.core.edrlog import EDR_LOG
from . import edrservicecheck
from . import edrservicefinder
from . import edrparkingsystemfinder
from . import edrsyssetlcheck
from . import edrsettlementfinder

class EDRStation:
    EDSM_STATIONS_CACHE = edr_cache_path('edsm_stations.v1.p')
    EDSM_MARKETS_CACHE = edr_cache_path('edsm_markets.v1.p')
    EDSM_SHIPYARDS_CACHE = edr_cache_path('edsm_shipyards.v1.p')
    EDSM_OUTFITTING_CACHE = edr_cache_path('edsm_outfitting.v1.p')

    def __init__(self, edrsystems):
        self.edrsystems = edrsystems
        self.server = edrsystems.server
        self.edsm_server = edrsystems.edsm_server
        self.reasonable_sc_distance = 1500
        self.reasonable_hs_radius = 50
        
        edr_config = edrconfig.EDR_CONFIG
        self.edsm_stations_cache = LRUCache.load(
            file_path=self.EDSM_STATIONS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_stations_max_age()
        )

        self.edsm_markets_cache = LRUCache.load(
            file_path=self.EDSM_MARKETS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_markets_max_age()
        )

        self.edsm_shipyards_cache = LRUCache.load(
            file_path=self.EDSM_SHIPYARDS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_shipyards_max_age()
        )

        self.edsm_outfitting_cache = LRUCache.load(
            file_path=self.EDSM_OUTFITTING_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_outfitting_max_age()
        )

    def save(self):
        self.edsm_stations_cache.save(self.EDSM_STATIONS_CACHE)
        self.edsm_markets_cache.save(self.EDSM_MARKETS_CACHE)
        self.edsm_shipyards_cache.save(self.EDSM_SHIPYARDS_CACHE)
        self.edsm_outfitting_cache.save(self.EDSM_OUTFITTING_CACHE)

    def stations_in_system(self, star_system):
        if not star_system:
            return None
        stations = self.edsm_stations_cache.get(star_system.lower())
        cached = self.edsm_stations_cache.has_key(star_system.lower())
        if cached or stations:
            EDR_LOG.debug("Stations for system {} are in the cache.".format(star_system))
            return stations

        stations = self.edsm_server.stations_in_system(star_system)
        if stations:
            self.edsm_stations_cache.set(star_system.lower(), stations)
            EDR_LOG.debug("Cached {}'s stations".format(star_system))
            return stations

    def station(self, star_system, station_name, station_type, pad_count_override=None):
        stations = self.stations_in_system(star_system)
        if not stations:
            return None
            
        for station in stations:
            if station["name"] == station_name:
                if pad_count_override and (station_type == "FleetCarrier" and pad_count_override > 16):
                    station = station.copy()
                    station["type"] = "squadron carrier"
                    if station.get("economy", "").lower() in ["fleetcarrier", "fleet carrier"]:
                        station["economy"] = "squadron carrier"
                
                return station
        
        worth_retrying_age = 60*60*6 
        if station_type in ["FleetCarrier", "SquadronCarrier"] and self.edsm_stations_cache.is_older_than(star_system.lower(), worth_retrying_age):
            # FleetCarrier are a bit more dynamic, so evict a lukewarm entry and get a new fresh one in case the info has been reflected since last time
            self.edsm_stations_cache.evict(star_system.lower())
            stations = self.stations_in_system(star_system)
            for station in stations:
                if station["name"] == station_name:
                    return station
        
        return None

    def fuzzy_stations(self, star_system, station_name):
        if station_name is None or station_name == "":
            return []

        stations = self.stations_in_system(star_system)
        if not stations:
            return []

        return [station for station in stations if (station_name.lower() in station["name"].lower())]

    def search_interstellar_factors(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStationServiceCheck('Interstellar Factors Contact')
        checker.name = 'Interstellar Factors Contact'
        checker.hint = 'Look for low security systems, or stations run by an anarchy faction regardless of system security'
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_raw_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRRawTraderCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_encoded_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDREncodedTraderCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_manufactured_trader(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRManufacturedTraderCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_black_market(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRBlackMarketCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_staging_station(self, star_system, callback, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStagingCheck(15)
        self.__search_a_service(star_system, callback, checker, with_large_pad = True, with_medium_pad = False, override_radius = 15, override_sc_distance = override_sc_distance, permits = permits, exclude_center = True)

    def search_parking_system(self, star_system, callback, override_rank = None):
        self.__search_a_parking(star_system, callback, override_radius = 25, override_rank = override_rank)

    def search_rrr_fc(self, star_system, callback, override_radius = None, permits = []):
        radius = override_radius if override_radius is not None and override_radius >= 0 else 0
        sc_dist = 10000
        checker = edrservicecheck.EDRFleetCarrierRRRCheck(radius, sc_dist)
        self.__search_a_service(star_system, callback, checker, override_radius = radius, permits = permits, shuffle_stations=True, override_sc_distance=sc_dist)

    def search_rrr(self, star_system, callback, override_radius = None, permits = []):
        radius = override_radius if override_radius is not None and override_radius >= 0 else 0
        sc_dist = 10000
        checker = edrservicecheck.EDRStationRRRCheck(radius, sc_dist)
        self.__search_a_service(star_system, callback, checker, override_radius = radius, permits = permits, shuffle_stations=True, override_sc_distance=sc_dist)

    def search_shipyard(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStationFacilityCheck('Shipyard')
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_outfitting(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStationFacilityCheck('Outfitting')
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_market(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRStationFacilityCheck('Market')
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_human_tech_broker(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRHumanTechBrokerCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_guardian_tech_broker(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = []):
        checker = edrservicecheck.EDRGuardianTechBrokerCheck()
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits)

    def search_offbeat_station(self, star_system, callback, with_large_pad = True, with_medium_pad = False, override_radius = 100, override_sc_distance = 100000, permits = []):
        override_sc_distance = override_sc_distance or 100000
        checker = edrservicecheck.EDROffBeatStationCheck(override_sc_distance)
        self.__search_a_service(star_system, callback, checker,  with_large_pad, with_medium_pad, override_radius, override_sc_distance, permits, shuffle_systems=True, shuffle_stations=True, exclude_center=True)

    def search_settlement(self, star_system, settlement, callback, override_radius = 100, override_sc_distance = 100000, permits = []):
        override_sc_distance = override_sc_distance or 100000
        checker = edrsyssetlcheck.EDRSettlementCheckerFactory.get_checker(settlement, override_sc_distance, self.edrsystems)
        if checker:
            self.__search_a_settlement(star_system, callback, checker, override_radius, override_sc_distance, permits, shuffle_systems=True, shuffle_planets=True, exclude_center=False)

    def __search_a_service(self, star_system, callback, checker, with_large_pad = True, with_medium_pad = False, override_radius = None, override_sc_distance = None, permits = [], shuffle_systems=False, shuffle_stations=False, exclude_center=False):
        sc_distance = override_sc_distance or self.reasonable_sc_distance
        sc_distance = max(250, sc_distance)
        radius = override_radius if override_radius is not None and override_radius >= 0 else self.reasonable_hs_radius
        radius = min(100, radius)

        finder = edrservicefinder.EDRServiceFinder(star_system, checker, self.edrsystems, callback)
        finder.with_large_pad(with_large_pad)
        finder.with_medium_pad(with_medium_pad)
        finder.within_radius(radius)
        finder.within_supercruise_distance(sc_distance)
        finder.permits_in_possession(permits)
        finder.shuffling(shuffle_systems, shuffle_stations)
        finder.ignore_center(exclude_center)
        finder.set_dlc(self.edrsystems.dlc_name)
        finder.start()

    def __search_a_parking(self, star_system, callback, override_radius = None, override_rank = None):
        rank = override_rank or 0
        rank = max(0, rank)
        radius = override_radius if override_radius is not None and override_radius >= 0 else self.reasonable_hs_radius
        radius = min(100, radius)

        finder = edrparkingsystemfinder.EDRParkingSystemFinder(star_system, self.edrsystems, callback)
        finder.within_radius(radius)
        finder.nb_to_pick(rank)
        finder.start()

    def __search_a_settlement(self, star_system, callback, checker, override_radius = None, override_sc_distance = None, permits = [], shuffle_systems=True, shuffle_planets=True, exclude_center=False, exclude_states=[], include_states=[]):
        sc_distance = override_sc_distance or self.reasonable_sc_distance
        sc_distance = max(250, sc_distance)
        radius = override_radius if override_radius is not None and override_radius >= 0 else self.reasonable_hs_radius
        radius = min(100, radius)

        finder = edrsettlementfinder.EDRSettlementFinder(star_system, checker, self.edrsystems, callback)
        finder.within_radius(radius)
        finder.within_supercruise_distance(sc_distance)
        finder.permits_in_possession(permits)
        finder.shuffling(shuffle_systems, shuffle_planets)
        finder.ignore_center(exclude_center)
        finder.ignore_states(exclude_states)
        finder.require_states(include_states)
        finder.set_dlc(self.edrsystems.dlc_name)
        finder.start()
