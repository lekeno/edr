"""
Cache management for EDR.
Extracted from edrsystems.py as part of refactoring for EDMC compliance.
"""

from edr.core import edrconfig
from edr.utils.lrucache import LRUCache
from edr.utils.edrpath import edr_cache_path

class EDRCacheManager:
    """
    Manages the lifecycle and persistence of EDR and EDSM caches.
    """
    
    # Cache file paths
    EDR_SYSTEMS_CACHE = edr_cache_path('systems.v5.p')
    EDR_RAW_MATERIALS_CACHE = edr_cache_path('raw_materials.v1.p')
    EDSM_BODIES_CACHE = edr_cache_path('edsm_bodies.v1.p')
    EDSM_SYSTEMS_CACHE = edr_cache_path('edsm_systems.v3.p')
    EDSM_STATIONS_CACHE = edr_cache_path('edsm_stations.v1.p')
    EDSM_SYSTEMS_WITHIN_RADIUS_CACHE = edr_cache_path('edsm_systems_radius.v2.p')
    EDSM_TRAFFIC_CACHE = edr_cache_path('edsm_traffic.v1.p')
    EDSM_DEATHS_CACHE = edr_cache_path('edsm_deaths.v1.p')
    EDSM_MARKETS_CACHE = edr_cache_path('edsm_markets.v1.p')
    EDSM_SHIPYARDS_CACHE = edr_cache_path('edsm_shipyards.v1.p')
    EDSM_OUTFITTING_CACHE = edr_cache_path('edsm_outfitting.v1.p')
    EDSM_SYSTEM_VALUES_CACHE = edr_cache_path('edsm_system_values.v1.p')
    EDR_NOTAMS_CACHE = edr_cache_path('notams.v2.p')
    EDR_SITREPS_CACHE = edr_cache_path('sitreps.v3.p')
    EDR_TRAFFIC_CACHE = edr_cache_path('traffic.v2.p')
    EDR_CRIMES_CACHE = edr_cache_path('crimes.v2.p')
    EDR_FC_REPORTS_CACHE = edr_cache_path('fc_reports.v1.p')
    EDR_FC_PRESENCE_CACHE = edr_cache_path('fc_presence.v1.p')
    EDR_FC_MATERIALS_CACHE = edr_cache_path('fc_materials.v1.p')
    EDR_FCS_CACHE = edr_cache_path('fcs.v1.p')

    def __init__(self):
        edr_config = edrconfig.EDR_CONFIG

        # --- EDR Caches ---
        self.systems_cache = LRUCache.load(
            file_path=self.EDR_SYSTEMS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.systems_max_age()
        )

        self.materials_cache = LRUCache.load(
            file_path=self.EDR_RAW_MATERIALS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.materials_max_age()
        )

        self.notams_cache = LRUCache.load(
            file_path=self.EDR_NOTAMS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.notams_max_age()
        )

        self.sitreps_cache = LRUCache.load(
            file_path=self.EDR_SITREPS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.sitreps_max_age()
        )

        self.crimes_cache = LRUCache.load(
            file_path=self.EDR_CRIMES_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.crimes_max_age()
        )

        # --- EDR Fleet Carrier (FC) Caches ---
        self.fc_reports_cache = LRUCache.load(
            file_path=self.EDR_FC_REPORTS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.fc_reports_max_age()
        )

        self.fc_presence_cache = LRUCache.load(
            file_path=self.EDR_FC_PRESENCE_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.fc_presence_max_age()
        )

        self.fc_materials_cache = LRUCache.load(
            file_path=self.EDR_FC_MATERIALS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.fc_materials_max_age()
        )

        self.fcs_cache = LRUCache.load(
            file_path=self.EDR_FCS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.fc_max_age()
        )

        self.traffic_cache = LRUCache.load(
            file_path=self.EDR_TRAFFIC_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.traffic_max_age()
        )

        # --- EDSM Caches ---
        self.edsm_systems_cache = LRUCache.load(
            file_path=self.EDSM_SYSTEMS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_systems_max_age()
        )

        self.edsm_bodies_cache = LRUCache.load(
            file_path=self.EDSM_BODIES_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_bodies_max_age()
        )

        self.edsm_stations_cache = LRUCache.load(
            file_path=self.EDSM_STATIONS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_stations_max_age()
        )

        self.edsm_systems_within_radius_cache = LRUCache.load(
            file_path=self.EDSM_SYSTEMS_WITHIN_RADIUS_CACHE,
            max_size=edr_config.edsm_within_radius_max_size(),
            max_age_seconds=edr_config.edsm_systems_max_age()
        )

        self.edsm_traffic_cache = LRUCache.load(
            file_path=self.EDSM_TRAFFIC_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_traffic_max_age()
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

        self.edsm_system_values_cache = LRUCache.load(
            file_path=self.EDSM_SYSTEM_VALUES_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_bodies_max_age()
        )

        self.edsm_deaths_cache = LRUCache.load(
            file_path=self.EDSM_DEATHS_CACHE,
            max_size=edr_config.lru_max_size(),
            max_age_seconds=edr_config.edsm_deaths_max_age()
        )

    def persist(self):
        """
        Save all caches to disk.
        """
        # --- EDR Caches ---
        if self.systems_cache:
            self.systems_cache.save(self.EDR_SYSTEMS_CACHE)

        if self.materials_cache:
            self.materials_cache.save(self.EDR_RAW_MATERIALS_CACHE)

        if self.notams_cache:
            self.notams_cache.save(self.EDR_NOTAMS_CACHE)

        if self.sitreps_cache:
            self.sitreps_cache.save(self.EDR_SITREPS_CACHE)

        if self.traffic_cache:
            self.traffic_cache.save(self.EDR_TRAFFIC_CACHE)

        if self.crimes_cache:
            self.crimes_cache.save(self.EDR_CRIMES_CACHE)

        # --- EDR Fleet Carrier (FC) Caches ---
        if self.fc_reports_cache:
            self.fc_reports_cache.save(self.EDR_FC_REPORTS_CACHE)

        if self.fc_materials_cache:
            self.fc_materials_cache.save(self.EDR_FC_MATERIALS_CACHE)

        if self.fc_presence_cache:
            self.fc_presence_cache.save(self.EDR_FC_PRESENCE_CACHE)

        if self.fcs_cache:
            self.fcs_cache.save(self.EDR_FCS_CACHE)

        # --- EDSM Caches ---
        if self.edsm_systems_cache:
            self.edsm_systems_cache.save(self.EDSM_SYSTEMS_CACHE)

        if self.edsm_bodies_cache:
            self.edsm_bodies_cache.save(self.EDSM_BODIES_CACHE)

        if self.edsm_system_values_cache:
            self.edsm_system_values_cache.save(self.EDSM_SYSTEM_VALUES_CACHE)

        if self.edsm_stations_cache:
            self.edsm_stations_cache.save(self.EDSM_STATIONS_CACHE)

        if self.edsm_systems_within_radius_cache:
            self.edsm_systems_within_radius_cache.save(self.EDSM_SYSTEMS_WITHIN_RADIUS_CACHE)

        if self.edsm_traffic_cache:
            self.edsm_traffic_cache.save(self.EDSM_TRAFFIC_CACHE)

        if self.edsm_deaths_cache:
            self.edsm_deaths_cache.save(self.EDSM_DEATHS_CACHE)
