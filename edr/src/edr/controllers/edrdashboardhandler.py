from edr.core.edrlog import EDR_LOG
from edr.core.edri18n import _

class EDRDashboardHandler:
    def __init__(self, edr_client):
        self.edr_client = edr_client
        self.ed_player = edr_client.player
        self.last_flags = 0
        self.last_flags2 = 0
        
    def dashboard_entry(self, cmdr, is_beta, entry):
        if entry.get("GuiFocus", 0) > 0:
            self.ed_player.in_game = True

        if 'Destination' in entry and self.ed_player.in_game:
            self.edr_client.destination_guidance(entry["Destination"])

        flags = entry.get('Flags', 0)
        flags2 = entry.get('Flags2', 0)

        if flags != self.last_flags or flags2 != self.last_flags2:
            self.last_flags = flags
            self.last_flags2 = flags2

            self._update_player_states(entry, flags, flags2)
            self._handle_environmental_checks(entry, flags)
        
        self._update_attitude_states(entry, flags, flags2)

    def _update_player_states(self, entry, flags, flags2):
        # Blue tunnel state
        self.ed_player.in_blue_tunnel((flags & edmc_data.FlagsFsdJump or flags2 & edmc_data.Flags2GlideMode))

        # Update on-foot location details
        self.ed_player.location.on_foot_location.update(flags2)

        # Determine if the player is on foot or in a vehicle
        on_foot_flags = (edmc_data.Flags2OnFoot | edmc_data.Flags2OnFootInStation | 
                         edmc_data.Flags2OnFootOnPlanet | edmc_data.Flags2OnFootInHangar | 
                         edmc_data.Flags2OnFootSocialSpace | edmc_data.Flags2OnFootExterior)
        
        if flags2 & on_foot_flags:
            self.ed_player.in_spacesuit()
            self.edr_client.on_foot()
            self._update_suit_stats(entry, flags2)
        else:
            self.edr_client.in_ship()
            self._update_vehicle_type(flags, flags2)
            self._update_vehicle_stats(entry, flags)

    def _handle_environmental_checks(self, entry, flags):
        # Handle Docking transition
        docked = bool(flags & edmc_data.FlagsDocked)
        if self.ed_player.is_docked and not docked:
            self.edr_client.ack_station_pending_reports()
        self.ed_player.docked(docked)

        # Danger & Hardpoints
        unsafe = bool(flags & edmc_data.FlagsIsInDanger)
        hp_deployed = bool(flags & edmc_data.FlagsHardpointsDeployed)
        self.ed_player.in_danger(unsafe)
        self.ed_player.hardpoints(hp_deployed)
        
        # Combat Reporting (Recon Box) logic
        if self.ed_player.recon_box.active and not (unsafe or hp_deployed):
            self.ed_player.recon_box.reset()
            self.edr_client.notify_with_details(_("EDR Central"), [_("Fight reporting disabled"), _("Looks like you are safe, and disengaged.")])
        
        if self.ed_player.in_normal_space() and self.ed_player.recon_box.process_signal(flags & edmc_data.FlagsLightsOn):
            if self.ed_player.recon_box.active:
                self.edr_client.notify_with_details(_("EDR Central"), [_("Fight reporting enabled"), _("Turn it off: flash your lights twice, or leave this area, or escape danger and retract hardpoints.")])
            else:
                self.edr_client.notify_with_details(_("EDR Central"), [_("Fight reporting disabled"), _("Flash your lights twice to re-enable.")])

    def _update_attitude_states(self, entry, flags, flags2):
        attitude_keys = { "Latitude", "Longitude", "Heading", "Altitude"}
        if entry.keys() < attitude_keys:
            return
        
        attitude = { key.lower():value for key,value in entry.items() if key in attitude_keys }
        if "altitude" in attitude:
            attitude["altitude"] /= 1000.0
        self.ed_player.update_attitude(attitude)
        if self.ed_player.body and self.ed_player.tracking_organic():
            self.edr_client.biology_guidance()
        elif not self.ed_player.planetary_destination and self.ed_player.body and self.ed_player.star_system:
            self.edr_client.try_custom_poi()

        if self.ed_player.planetary_destination:
            self.edr_client.show_navigation()

    def _update_suit_stats(self, entry, flags2):
        if not self.ed_player.spacesuit:
            return

        self.ed_player.spacesuit.low_health = flags2 & edmc_data.Flags2LowHealth
        self.ed_player.spacesuit.low_oxygen = flags2 & edmc_data.Flags2LowOxygen
        
        if (entry.get("Oxygen", None)):
            self.ed_player.spacesuit.oxygen = entry["Oxygen"]
        
        if (entry.get("Health", None)):
            self.ed_player.spacesuit.health = entry["Health"]

    def _update_vehicle_stats(self, entry, flags):
        if not self.ed_player.piloted_vehicle:
            return

        self.ed_player.piloted_vehicle.over_heating = flags & edmc_data.FlagsOverHeating
        self.ed_player.piloted_vehicle.low_fuel = bool(flags & edmc_data.FlagsLowFuel)
        fuel = entry.get('Fuel', None)
        if fuel:
            main = fuel.get('FuelMain', self.ed_player.piloted_vehicle.fuel_level)
            reservoir = fuel.get('FuelReservoir', 0)
            self.ed_player.piloted_vehicle.fuel_level = main + reservoir

    def _update_vehicle_type(self, flags, flags2):
        if (flags & edmc_data.FlagsInMainShip) and not (flags2 & edmc_data.Flags2InTaxi):
            self.ed_player.in_mothership()
        
        if (flags & edmc_data.FlagsInFighter):
            self.ed_player.in_slf()

        if (flags & edmc_data.FlagsInSRV):
            self.ed_player.in_srv()
        
        if (flags2 & edmc_data.Flags2InTaxi):
            self.ed_player.in_taxi()

    def _pips(self, entry):
        if self.ed_player.pips(entry.get("Pips", None)) and self.ed_player.piloted_vehicle:
            shield_res = self.ed_player.piloted_vehicle.shield_resistances()
            hull_res = self.ed_player.piloted_vehicle.hull_resistances()
            dps = self.ed_player.piloted_vehicle.damage_per_shot()
            details = [
                "S{:0.1f} T{:0.2f}% K{:0.2f}% E{:0.2f}%".format(self.ed_player.piloted_vehicle.shield_strength(), shield_res.thermal*100, shield_res.kinetic*100, shield_res.explosive*100),
                "H{:0.1f} T{:0.2f}% K{:0.2f}% E{:0.2f}%".format(self.ed_player.piloted_vehicle.hull_strength(), hull_res.thermal*100, hull_res.kinetic*100, hull_res.explosive*100),
                "A{:0.1f} T{:0.2f}  K{:0.2f}  E{:0.2f}".format(dps["absolute"], dps["thermal"], dps["kinetic"], dps["explosive"], dps["caustic"])
            ]
            self.edr_client.notify_with_details("[Debug] O/D stats", details, clear_before=True)