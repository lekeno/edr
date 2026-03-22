class EDRSquadronMember:
    """
    Represents a squadron member info.
    """
    SOMEWHAT_TRUSTED_LEVEL = {"rank": "wingman", "level": 100}
    FULLY_TRUSTED_LEVEL = {"rank": "co-pilot", "level": 300}

    def __init__(self, squadron_dict):
        """
        Initialize based on squadron dictionary.

        Args:
            squadron_dict (dict): Squadron info.
        """
        self.name = squadron_dict.get("squadronName", None)
        self.inara_id = squadron_dict.get("squadronId", None)
        self.rank = squadron_dict.get("squadronRank", None)
        self.heartbeat = squadron_dict.get("heartbeat", None)
        self.level = squadron_dict.get("squadronLevel", None)

    def is_somewhat_trusted(self):
        """
        Returns:
            bool: True if somewhat trusted ranking.
        """
        return self.level >= EDRSquadronMember.SOMEWHAT_TRUSTED_LEVEL["level"]

    def is_fully_trusted(self):
        """
        Returns:
            bool: True if fully trusted ranking.
        """
        return self.level >= EDRSquadronMember.FULLY_TRUSTED_LEVEL["level"]

    def info(self):
        """
        Returns:
            dict: Squadron info dictionary.
        """
        return {
            "squadronName": self.name,
            "squadronId": self.inara_id,
            "squadronRank": self.rank,
            "squadronLevel": self.level
        }
