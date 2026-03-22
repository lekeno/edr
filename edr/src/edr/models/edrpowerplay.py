from edr.utils.edtime import EDTime

class EDRPowerplay:
    """
    Manages powerplay affiliation and checks.
    """
    POWERS_AFFILIATION = {
        "a_lavigny-duval": "Empire",
        "arissa lavigny duval": "Empire",
        "aisling_duval": "Empire",
        "aisling duval": "Empire",
        "archon_delaine": None,
        "archon delaine": None,
        "denton_patreus": "Empire",
        "denton patreus": "Empire",
        "edmund_mahon": "Alliance",
        "edmund mahon": "Alliance",
        "felicia_winters": "Federation",
        "felicia winters": "Federation",
        "li_yong-rui": None,
        "li yong-rui": None,
        "pranav_antal": None,
        "pranav antal": None,
        "yuri_grom": None,
        "yuri grom": None,
        "zachary_hudson": "Federation",
        "zachary hudson": "Federation",
        "zemina_torval": "Empire",
        "zemina torval": "Empire",
        "nakato_kaine": "Alliance",
        "nakato kaine": "Alliance",
        "jerome_archer": "Federation",
        "jerome archer": "Federation",
    }

    POWERS_PRETTY_PRINT = {
        "a_lavigny-duval": "Lavigny",
        "aisling_duval": "Aisling",
        "archon_delaine": "Archon",
        "denton_patreus": "Patreus",
        "edmund_mahon": "Mahon",
        "felicia_winters": "Winters",
        "li_yong-rui": "Li Yong-rui",
        "pranav_antal": "Antal",
        "yuri_grom": "Yuri",
        "zachary_hudson": "Zachary",
        "zemina_torval": "Zemina",
        "nakato_kaine": "Nakato",
        "jerome_archer": "Jerome",
        "independent": "Independent",
        "unknown": "Unknown"
    }

    def __init__(self, pledged_to, time_pledged):
        """
        Initialize powerplay info.

        Args:
            pledged_to (str): Name of the power.
            time_pledged (int): Timestamp when pledged? or duration? (Assuming timestamp based on calc)
        """
        self.pledged_to = pledged_to
        self.since = EDTime.py_epoch_now() - time_pledged

    def is_enemy(self, power):
        """
        Check if another power is an enemy.

        Args:
            power (str): The other power's name.

        Returns:
            bool: True if enemy, False otherwise.
        """
        power = power.lower()
        if not (self.pledged_to in self.POWERS_AFFILIATION and power in self.POWERS_AFFILIATION):
            return False
        my_affiliation = self.POWERS_AFFILIATION[self.pledged_to]
        their_affiliation = self.POWERS_AFFILIATION[power]
        return my_affiliation != their_affiliation if my_affiliation else True

    def pretty_print(self):
        """
        Returns:
            str: Pretty printed power name.
        """
        if self.pledged_to in self.POWERS_PRETTY_PRINT:
            return self.POWERS_PRETTY_PRINT[self.pledged_to]
        return self.pledged_to

    def canonicalize(self):
        """
        Returns:
            str: Canonicalized power name (lowercase, snake_case).
        """
        if self.pledged_to:
            return self.pledged_to.lower().replace(" ", "_")
        return ""

    def time_pledged(self):
        """
        Returns:
            int: Duration pledged in seconds.
        """
        return EDTime.py_epoch_now() - self.since

    def is_somewhat_trusted(self):
        """
        Returns:
            bool: True if trusted.
        """
        return False
        # TODO return true if enough time has passed (parameterize)

    def is_fully_trusted(self):
        """
        Returns:
            bool: True if fully trusted.
        """
        return False
        # TODO return true if enough time has passed (parameterize)


class EDRPowerplayUnknown(EDRPowerplay):
    """
    Represents an unknown powerplay affiliation.
    """
    def __init__(self):
        """
        Initialize unknown powerplay.
        """
        super().__init__("Unknown", EDTime.py_epoch_now())

    def is_enemy(self, power):
        """
        Check if enemy (always False for distinct unknown).
        """
        return False

    def pretty_print(self):
        """
        Returns:
            str: 'Unknown'.
        """
        return "Unknown"

    def canonicalize(self):
        """
        Returns:
            str: 'unknown'.
        """
        return "unknown"

    def time_pledged(self):
        """
        Returns:
            int: 0.
        """
        return 0

    def is_somewhat_trusted(self):
        return False

    def is_fully_trusted(self):
        return False
