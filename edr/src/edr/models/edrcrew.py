from edr.utils.edtime import EDTime

class EDRCrew:
    """
    Manages crew members for a pilot.
    """
    def __init__(self, captain):
        """
        Initialize the crew.

        Args:
            captain (str): The captain's name.
        """
        self.captain = captain
        self.creation = EDTime.py_epoch_now()
        self.members = {captain: self.creation}

    def add(self, crew_member):
        """
        Add a crew member.

        Args:
            crew_member (str): Name of the crew member.

        Returns:
            bool: True if added, False if already present.
        """
        if crew_member in self.members:
            return False
        self.members[crew_member] = EDTime.py_epoch_now()
        return True

    def remove(self, crew_member):
        """
        Remove a crew member.

        Args:
            crew_member (str): Name of the crew member.

        Returns:
            bool: True if removed, False if not found.
        """
        try:
            del self.members[crew_member]
            return True
        except KeyError:
            return False

    def all_members(self):
        """
        Get all crew members.

        Returns:
            list: List of crew member names.
        """
        return list(self.members.keys())

    def disband(self):
        """
        Disband the crew.
        """
        self.members = {}
        self.captain = None
        self.creation = None

    def is_captain(self, member):
        """
        Check if a member is the captain.

        Args:
            member (str): Member name.

        Returns:
            bool: True if captain.
        """
        return member == self.captain

    def duration(self, member):
        """
        Get duration of membership for a crew member.

        Args:
            member (str): Member name.

        Returns:
            int: Duration in seconds.
        """
        if member not in self.members:
            return 0
        now = EDTime.py_epoch_now()
        then = self.members[member]
        return now - then
