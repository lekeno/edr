from __future__ import absolute_import

from collections import deque
from edtime import EDTime
from lrucache import LRUCache
from edrconfig import EDRConfig

class EDRBountyHuntingStats(object):
    def __init__(self):
        self.max = 0
        self.previous_max = 0
        self.min = 100.0
        self.previous_min = 0
        self.sum_scanned = 0
        self.sum_awarded = 0
        self.distribution = {"last_index": 0, "bins": [0]*25}
        self.scanned_nb = 0
        self.awarded_nb = 0
        self.awarded_bounties = deque(maxlen=20)
        self.scans = deque(maxlen=20)
        self.efficiency = deque(maxlen=20)
        self.max_efficiency = 5000000
        self.max_normal_bounty = 350000 # appears to be the highest bounty per faction for NPC
        now = EDTime.py_epoch_now()
        self.start = now
        self.current = now
        edr_config = EDRConfig()
        self.scans_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.last = {"timestamp": now, "bounty": None, "name": None, "distribution_index": 0}

    def reset(self):

        self.max = 0
        self.previous_max = 0
        self.min = 100.0
        self.previous_min = 0
        self.sum_scanned = 0
        self.sum_awarded = 0
        self.distribution = {"last_index": 0, "bins": [0]*25}
        self.scanned_nb = 0
        self.awarded_nb = 0
        self.awarded_bounties = deque(maxlen=20)
        self.scans = deque(maxlen=20)
        self.efficiency = deque(maxlen=20)
        self.max_efficiency = 1000000
        now = EDTime.py_epoch_now()
        self.start = now
        self.current = now
        edr_config = EDRConfig()
        self.scans_cache = LRUCache(edr_config.lru_max_size(), edr_config.blips_max_age())
        self.last = {"timestamp": now, "bounty": None, "name": None, "distribution_index": 0}

    def dummify(self):
        self.reset()
        
        events = [
                { "delta":0, "event":"ShipTargeted", "TargetLocked":True, "Ship":"ferdelance", "Ship_Localised":"Fer-de-Lance", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Marita Raja;", "PilotName_Localised":"Marita Raja", "PilotRank":"Deadly", "ShieldHealth":3.870541, "HullHealth":52.374279, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":157095 },
                { "delta":20, "event":"Bounty", "Rewards":[ { "Faction":"Sirius Corporation", "Reward":157095 } ], "Target":"ferdelance", "Target_Localised":"Fer-de-Lance", "TotalReward":157095, "VictimFaction":"Sirius Silver Mafia", "SharedWithOthers":1 },
                { "delta":10, "event":"ShipTargeted", "TargetLocked":True, "Ship":"ferdelance", "Ship_Localised":"Fer-de-Lance", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Professor Argaty;", "PilotName_Localised":"Professor Argaty", "PilotRank":"Deadly", "ShieldHealth":11.246920, "HullHealth":100.000000, "Faction":"Sirius Corporation", "LegalStatus":"Wanted", "Bounty":177690 },
                { "delta":76, "event":"ShipTargeted", "TargetLocked":True, "Ship":"typex", "Ship_Localised":"Alliance Chieftain", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Tangle Iso;", "PilotName_Localised":"Tangle Iso", "PilotRank":"Deadly", "ShieldHealth":93.456848, "HullHealth":99.907257, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":110932 },
                { "delta":18, "event":"ShipTargeted", "TargetLocked":True, "Ship":"typex", "Ship_Localised":"Alliance Chieftain", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Tangle Iso;", "PilotName_Localised":"Tangle Iso", "PilotRank":"Deadly", "ShieldHealth":20.290726, "HullHealth":57.679016, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":111232 },
                { "delta":1, "event":"ShipTargeted", "TargetLocked":True, "Ship":"typex", "Ship_Localised":"Alliance Chieftain", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Tangle Iso;", "PilotName_Localised":"Tangle Iso", "PilotRank":"Deadly", "ShieldHealth":30.054546, "HullHealth":39.219852, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":111532 },
                { "delta":2, "event":"ShipTargeted", "TargetLocked":True, "Ship":"typex", "Ship_Localised":"Alliance Chieftain", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Tangle Iso;", "PilotName_Localised":"Tangle Iso", "PilotRank":"Deadly", "ShieldHealth":30.312126, "HullHealth":39.113632, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":111532 },
                { "delta":60, "event":"ShipTargeted", "TargetLocked":True, "Ship":"typex", "Ship_Localised":"Alliance Chieftain", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Tangle Iso;", "PilotName_Localised":"Tangle Iso", "PilotRank":"Deadly", "ShieldHealth":31.023048, "HullHealth":39.113632, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":111532, "Subsystem":"$int_powerplant_size6_class5_name;", "Subsystem_Localised":"Power Plant", "SubsystemHealth":99.030571 },
                { "delta":53, "event":"ShipTargeted", "TargetLocked":True, "Ship":"vulture", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Shayne Fotheringhame;", "PilotName_Localised":"Shayne Fotheringhame", "PilotRank":"Deadly", "ShieldHealth":100.000000, "HullHealth":100.000000, "Faction":"Sirius Free", "LegalStatus":"Wanted", "Bounty":92070 },
                { "delta":1, "event":"ShipTargeted", "TargetLocked":True, "Ship":"vulture", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Shayne Fotheringhame;", "PilotName_Localised":"Shayne Fotheringhame", "PilotRank":"Deadly", "ShieldHealth":0.000000, "HullHealth":79.630348, "Faction":"Sirius Free", "LegalStatus":"Wanted", "Bounty":92370, "Subsystem":"$int_lifesupport_size3_class3_name;", "Subsystem_Localised":"Life Support", "SubsystemHealth":100.000000 },
                { "delta":61, "event":"ShipTargeted", "TargetLocked":True, "Ship":"vulture", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Shayne Fotheringhame;", "PilotName_Localised":"Shayne Fotheringhame", "PilotRank":"Deadly", "ShieldHealth":0.000000, "HullHealth":79.303833, "Faction":"Sirius Free", "LegalStatus":"Wanted", "Bounty":92370, "Subsystem":"$int_hyperdrive_size4_class3_name;", "Subsystem_Localised":"FSD", "SubsystemHealth":97.512024 },
                { "delta":5, "event":"Bounty", "Rewards":[ { "Faction":"Sirius Corporation", "Reward":92370 } ], "Target":"vulture", "TotalReward":92370, "VictimFaction":"Sirius Free", "SharedWithOthers":1 },
                { "delta":8, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Test;", "PilotName_Localised":"Test", "PilotRank":"Deadly", "ShieldHealth":100.000000, "HullHealth":99.988197, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":166185 },
                { "delta":57, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Torben;", "PilotName_Localised":"Torben", "PilotRank":"Deadly", "ShieldHealth":100.000000, "HullHealth":100.000000, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":146340 },
                { "delta":8, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Torben;", "PilotName_Localised":"Torben", "PilotRank":"Deadly", "ShieldHealth":0.000000, "HullHealth":84.573822, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":344782, "Subsystem":"$int_powerplant_size7_class5_name;", "Subsystem_Localised":"Power Plant", "SubsystemHealth":99.765564 },
                { "delta":2, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Torben;", "PilotName_Localised":"Torben", "PilotRank":"Deadly", "ShieldHealth":0.000000, "HullHealth":63.765450, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":344782, "Subsystem":"$hpt_multicannon_gimbal_large_name;", "Subsystem_Localised":"Multi-Cannon", "SubsystemHealth":100.000000 },
                { "delta":1, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Torben;", "PilotName_Localised":"Torben", "PilotRank":"Deadly", "ShieldHealth":0.000000, "HullHealth":55.865925, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":344782, "Subsystem":"$int_shieldcellbank_size6_class5_name;", "Subsystem_Localised":"Shield Cell Bank", "SubsystemHealth":98.095177 },
                { "delta":1, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Torben;", "PilotName_Localised":"Torben", "PilotRank":"Deadly", "ShieldHealth":0.000000, "HullHealth":54.469265, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":344782, "Subsystem":"$int_powerdistributor_size7_class5_name;", "Subsystem_Localised":"Power Distributor", "SubsystemHealth":97.202393 },
                { "delta":2, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Torben;", "PilotName_Localised":"Torben", "PilotRank":"Deadly", "ShieldHealth":0.000000, "HullHealth":50.422470, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":344782, "Subsystem":"$int_lifesupport_size4_class5_name;", "Subsystem_Localised":"Life Support", "SubsystemHealth":99.373184 },
                { "delta":25, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Torben;", "PilotName_Localised":"Torben", "PilotRank":"Deadly", "ShieldHealth":0.824910, "HullHealth":45.207794, "Faction":"Sirius Silver Mafia", "LegalStatus":"Wanted", "Bounty":344782, "Subsystem":"$int_hyperdrive_size5_class3_name;", "Subsystem_Localised":"FSD", "SubsystemHealth":99.515030 },
                { "delta":12, "event":"Bounty", "Rewards":[ { "Faction":"Sirius Corporation", "Reward":147240 }, { "Faction":"Sirius Free", "Reward":93420 }, { "Faction":"League of Caihe", "Reward":104422 } ], "Target":"python", "TotalReward":345082, "VictimFaction":"Sirius Silver Mafia", "SharedWithOthers":3 },
                { "delta":2, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Nimrood;", "PilotName_Localised":"Nimrood", "PilotRank":"Deadly", "ShieldHealth":100.000000, "HullHealth":100.000000, "Faction":"HIP 495 Crimson Raiders", "LegalStatus":"Wanted", "Bounty":195412 },
                { "delta":5, "event":"ShipTargeted", "TargetLocked":True, "Ship":"python", "ScanStage":3, "PilotName":"$npc_name_decorate:#name=Nimrood;", "PilotName_Localised":"Nimrood", "PilotRank":"Deadly", "ShieldHealth":100.000000, "HullHealth":100.000000, "Faction":"HIP 495 Crimson Raiders", "LegalStatus":"Wanted", "Bounty":195412 }
        ]

        faketime = EDTime()
        faketime.rewind(8*60)
        self.start -= 8*60
        for entry in events:
            faketime.advance(entry["delta"])
            entry["timestamp"] = faketime.as_journal_timestamp()
            if entry.get("event", None) == "ShipTargeted":
                self.scanned(entry)
            elif entry.get("event", None) == "Bounty":
                self.awarded(entry)
    
    def scanned(self, entry):
        if entry.get("event", None) != "ShipTargeted":
            return False
        if entry.get("ScanStage", 0) < 3:
            return False
        
        raw_pilot_name = entry.get("PilotName", None)
        if not raw_pilot_name:
            return False

        bounty = entry.get("Bounty", 0)
        now = EDTime.py_epoch_now()
        index = min(int(round(bounty/self.max_normal_bounty * (len(self.distribution["bins"])-1), 0)), len(self.distribution["bins"])-1)
        self.last = {
            "timestamp": now,
            "bounty": bounty,
            "name": entry.get("PilotName_Localised", ""),
            "distribution_index": index
        }

        if self.__probably_previously_scanned(entry):
            return False
        
        self.scans_cache.set(raw_pilot_name, entry)
        self.current = now
        if bounty <= 0:
            return False
            
        self.scanned_nb += 1
        self.__update_efficiency()
        
        self.sum_scanned += bounty
        self.previous_max = self.max
        self.previous_min = self.min
        self.max = max(self.max, bounty)
        self.min = min(self.min, bounty)
        self.distribution["last_index"] = index
        self.distribution["bins"][index] += 1
        self.scans.append((now, bounty))

    def __probably_previously_scanned(self, entry):
        raw_pilot_name = entry.get("PilotName", None)
        if not raw_pilot_name:
            return False
        
        last_scan = self.scans_cache.get(raw_pilot_name)
        if not last_scan:
            return False
        return (entry["LegalStatus"] == last_scan["LegalStatus"]) and (entry.get("Bounty", 0) == last_scan.get("Bounty",0))
    
    def awarded(self, entry):
        if entry.get("event", None) != "Bounty":
            return
        now = EDTime.py_epoch_now()
        self.current = now
        
        total_rewards = 0
        rewards = entry.get("Rewards", [])
        for reward in rewards:
            total_rewards += reward.get("Reward", 0)
            
        self.sum_awarded += total_rewards
        self.awarded_nb += 1
        self.awarded_bounties.append((now, total_rewards))
        self.__update_efficiency()

    def credits_per_hour(self):
        now = EDTime.py_epoch_now()
        self.current = now
        elapsed_time = self.current - self.start
        if elapsed_time:
            return self.sum_awarded / (elapsed_time / 3600.0)
        return 0
    
    def bounty_average(self):
        return (self.sum_scanned / self.scanned_nb) if self.scanned_nb else 0.0
    
    def reward_average(self):
        return (self.sum_awarded / self.awarded_nb) if self.scanned_nb else 0.0

    def __update_efficiency(self):
        now = EDTime.py_epoch_now()
        efficiency = self.credits_per_hour()
        self.efficiency.append((now, efficiency))
        self.max_efficiency = max(self.max_efficiency, efficiency)

    def __repr__(self):
        return str(self.__dict__)