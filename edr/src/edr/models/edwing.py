from edr.utils.edtime import EDTime

class EDWing:
    """
    Manages wingmates (team).
    """
    def __init__(self, wingmates=set()):
        """
        Initialize wing.

        Args:
            wingmates (set): Set of wingmate names.
        """
        self.wingmates = wingmates.copy()
        self.timestamp = None
        self.last_check_timestamp = None
        self._touched = False

    def leave(self):
        """
        Leave the wing.
        """
        self.wingmates = set()
        self._touch()

    def join(self, others):
        """
        Join a wing.

        Args:
            others (list): List of wingmate names.
        """
        self.wingmates = set(others)
        self._touch()

    def add(self, other):
        """
        Add a wingmate.

        Args:
            other (str): Name of wingmate.
        """
        self.wingmates.add(other)
        self._touch()

    def formed(self):
        """
        Returns:
            bool: True if wing is formed.
        """
        return len(self.wingmates) > 0

    def _touch(self):
        now = EDTime.py_epoch_now()
        self.timestamp = now
        self._touched = True

    def noteworthy_changes_json(self, instance):
        """
        Get JSON of noteworthy changes in wing status.

        Args:
            instance (EDInstance): Current instance info.

        Returns:
            list: List of changes.
        """
        changes = []
        if not self._touched:
            for wingmate in self.wingmates:
                if instance.player(wingmate) is None:
                    continue
                blip = instance.blip(wingmate)
                if not blip:
                    continue
                timestamp = list(blip.keys())[0] # blip is {timestamp: entry}
                if self.last_check_timestamp is None or timestamp >= self.last_check_timestamp:
                    changes.append({"cmdr": wingmate, "instanced": True})
        elif self.last_check_timestamp is None or self.timestamp is None or self.timestamp >= self.last_check_timestamp:
            changes = [{"cmdr": wingmate, "instanced": instance.player(wingmate) is not None} for wingmate in self.wingmates]
        self._touched = False
        now = EDTime.py_epoch_now()
        self.last_check_timestamp = now
        return changes
