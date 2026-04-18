from .edpilot import EDPilot
from edr.core.edrlog import EDR_LOG

class EDPlayer(EDPilot):
    """
    Represents a player (Commander).
    """
    def __init__(self, name, rank=None):
        """
        Initialize the player.

        Args:
            name (str): Commander name.
            rank (int, optional): Rank.
        """
        super().__init__(name, rank)
        self.blue_tunnel = False

    def json(self):
        """
        Returns:
            dict: JSON representation of player.
        """
        blob = {
            "cmdr": self.name,
            "timestamp": self.timestamp * 1000,
            "wanted": self.wanted,
            "bounty": self.bounty,
            "power": self.powerplay.canonicalize() if self.powerplay else '',
            "enemy": self.enemy
        }

        if (self.piloted_vehicle):
            blob["ship"] = self.piloted_vehicle.json()
        else:
            blob["spacesuit"] = self.spacesuit.json()

        if self.sqid:
            blob["sqid"] = self.sqid
        return blob

    def is_human(self):
        """
        Returns:
            bool: True (always human).
        """
        return True

    def to_normal_space(self):
        """
        Transition to normal space.
        """
        self.blue_tunnel = False
        super(EDPlayer, self).to_normal_space()

    def to_super_space(self):
        """
        Transition to supercruise.
        """
        self.blue_tunnel = False
        super(EDPlayer, self).to_super_space()

    def to_hyper_space(self):
        """
        Transition to hyperspace.
        """
        self.blue_tunnel = True
        super(EDPlayer, self).to_hyper_space()

    def in_blue_tunnel(self, tunnel=True):
        """
        Update blue tunnel status (hyperspace tunnel).

        Args:
            tunnel (bool): True if in tunnel.
        """
        if tunnel != self.blue_tunnel:
            EDR_LOG.debug("Blue Tunnel update: {old} vs. {new}".format(old=self.blue_tunnel, new=tunnel))
        self.blue_tunnel = tunnel

    def is_trusted_by_squadron(self):
        """
        Returns:
            bool: True if trusted by squadron.
        """
        if self.is_lone_wolf():
            return False
        return self.squadron.is_somewhat_trusted()

    def squadron_trusted_rank(self):
        """
        Returns:
            str: Rank required for trust.
        """
        from .edrsquadron import EDRSquadronMember
        return EDRSquadronMember.SOMEWHAT_TRUSTED_LEVEL["rank"]

    def squadron_empowered_rank(self):
        """
        Returns:
            str: Rank required for empowerment.
        """
        from .edrsquadron import EDRSquadronMember
        return EDRSquadronMember.FULLY_TRUSTED_LEVEL["rank"]

    def is_empowered_by_squadron(self):
        """
        Returns:
            bool: True if empowered by squadron.
        """
        if self.is_lone_wolf():
            return False
        return self.squadron.is_fully_trusted()

    def is_trusted_by_power(self):
        """
        Returns:
            bool: True if trusted by power.
        """
        if self.is_independent():
            return False
        return self.powerplay.is_somewhat_trusted()

    def is_empowered_by_power(self):
        """
        Returns:
            bool: True if empowered by power (or independent).
        """
        if self.is_independent():
            return True
        return self.powerplay.is_fully_trusted()
