from edr.utils.edtime import EDTime


class EDRAfkDetector:
    """
    Detects if a commander is AFK (Away From Keyboard) based on recent events.
    """

    PASSIVE_EVENTS = {
        "Died", "HeatDamage", "FighterDestroyed", "HeatWarning", "HullDamage",
        "Interdicted", "ShieldState", "SRVDestroyed", "UnderAttack",
        "CommunityGoal", "CommunityGoalReward", "MissionFailed",
        "MissionRedirected", "ReceiveText", "Fileheader", "Friends",
        "DisbandedSquadron", "InvitedToSquadron", "KickedFromSquadron",
        "SquadronDemotion", "SquadronPromotion", "WonATrophyForSquadron",
        "Continued", "CrewMemberJoins", "CrewMemberQuits", "CrimeVictim",
        "Music", "NpcCrewPaidWage", "WingInvite"
    }

    def __init__(self):
        """Initialize the AFK detector with a threshold."""
        self.inactive_threshold_seconds = 60 * 5
        self.last_active_event = None

    def process(self, event):
        """Process an event to update the last active timestamp.

        Args:
            event (dict): The journal event dictionary.
        """
        if event["event"] not in self.PASSIVE_EVENTS:
            self.last_active_event = event

    def is_afk(self):
        """Check if the commander is considered AFK.

        Returns:
            bool: True if inactive for longer than the threshold, False otherwise.
        """
        if self.last_active_event is None:
            # unclear
            return True

        last_active = EDTime()
        last_active.from_journal_timestamp(self.last_active_event["timestamp"])

        now = EDTime.py_epoch_now()
        return (now - last_active.as_py_epoch()) > self.inactive_threshold_seconds
