import edtime

class EDRAfkDetector(object):
    PASSIVE_EVENTS = ["Died", "HeatDamage", "FighterDestroyed", "HeatWarning", "HullDamage", "Interdicted", "ShieldState", "SRVDestroyed", "UnderAttack", "CommunityGoal", "CommunityGoalReward", "MissionFailed", "MissionRedirected", "ReceiveText"]

    def __init__(self):
        self.inactive_threshold_seconds = 60*5
        self.last_active_event = None

    def process(self, event):
        if event["event"] not in self.PASSIVE_EVENTS:
            self.last_active_event = event

    def is_afk(self):
        if self.last_active_event is None:
            # unclear
            return True

        last_active = edtime.EDTime()
        last_active.from_journal_timestamp(self.last_active_event["timestamp"])

        now = edtime.EDTime.py_epoch_now()
        return (now - last_active.as_py_epoch()) > self.inactive_threshold_seconds
