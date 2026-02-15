import datetime
import os

from edr.utils.lrucache import LRUCache  # EDR_INTERNAL
from edr.core.edrconfig import EDR_CONFIG  # EDR_INTERNAL
from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL
from edr.utils.edtime import EDTime  # EDR_INTERNAL
from .edentities import EDFineOrBounty  # EDR_INTERNAL
from edr.core.edri18n import _, _c  # EDR_INTERNAL


class EDRLegalRecords:
    """
    Manages legal records (bounties, fines) for commanders.
    Uses an LRU cache to store fetched records.
    """
    edr_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    EDR_LEGAL_RECORDS_CACHE = os.path.join(
        edr_root, 'cache', 'legal_records.v3.p'
    )

    def __init__(self, server):
        """
        Initialize the legal records manager.

        Args:
            server (EDRServer): The EDR server instance.
        """
        self.server = server
        self.timespan = None
        self.records_check_interval = None
        config = EDR_CONFIG

        self.records = LRUCache.load(
            file_path=self.EDR_LEGAL_RECORDS_CACHE,
            max_size=config.lru_max_size(),
            max_age_seconds=config.legal_records_max_age()
        )

        self.timespan = config.legal_records_recent_threshold()
        self.records_check_interval = config.legal_records_check_interval()

    def persist(self):
        """
        Save the cache to disk.
        """
        if self.records:
            self.records.save(self.EDR_LEGAL_RECORDS_CACHE)

    def summarize(self, cmdr_id):
        """
        Fetch and summarize legal records for a specific commander.

        Args:
            cmdr_id (str): The ID/Name of the commander.

        Returns:
            dict: A dictionary containing the summary overview and stats, or None.
        """
        if not cmdr_id:
            EDR_LOG.info(f"No cmdr_id, no records for {cmdr_id}")
            return None

        self._update_records_if_stale(cmdr_id)

        record_entry = self.records.peek(cmdr_id)
        records = record_entry.get("records") if record_entry and isinstance(record_entry, dict) else None

        if not records:
            EDR_LOG.info(f"No legal records for {cmdr_id}")
            return None

        EDR_LOG.info(f"Got legal records for {cmdr_id}")
        overview = None
        (clean, wanted, bounties, recent_stats) = self._process(records)
        timespan = EDTime.pretty_print_timespan(self.timespan, short=True, verbose=True)
        max_b_str = ""
        last_b_str = ""

        if recent_stats["maxBounty"]:
            max_bounty = EDFineOrBounty(recent_stats["maxBounty"]).pretty_print()
            max_b_str = _(", max={} cr").format(max_bounty)

        if "last" in recent_stats and recent_stats["last"].get("value", None) and (recent_stats["last"].get("starSystem", "") not in ["", "unknown", "Unknown"]):
            tminus = EDTime.t_minus(recent_stats["last"]["timestamp"], short=True)
            last_bounty = EDFineOrBounty(recent_stats["last"]["value"]).pretty_print()
            last_b_str = _(", last: {} cr in {} {}").format(last_bounty, recent_stats["last"]["starSystem"], tminus)

        # Translators: this is an overview of a cmdr's recent legal history for the 'last {}' days, number of clean and wanted scans, and optionally max and last bounties
        overview = _("[Past {}] clean:{} / wanted:{}{}{}").format(
            timespan, recent_stats["clean"], recent_stats["wanted"], max_b_str, last_b_str
        )
        return {"overview": overview, "clean": clean, "wanted": wanted, "bounties": bounties}

    def _are_records_stale_for_cmdr(self, cmdr_id):
        """
        Check if the records for a commander are stale.

        Args:
            cmdr_id (str): Commander ID.

        Returns:
            bool: True if stale, False otherwise.
        """
        record_entry = self.records.peek(cmdr_id)

        if record_entry is None:
            return True

        last_updated = record_entry.get("last_updated")

        if last_updated is None:
            return True

        now = datetime.datetime.now()
        time_since_update = (now - last_updated).total_seconds()
        return time_since_update > self.records_check_interval

    def _update_records_if_stale(self, cmdr_id):
        """
        Update local cache from server if records are stale.

        Args:
            cmdr_id (str): Commander ID.

        Returns:
            bool: True if updated, False otherwise.
        """
        updated = False

        if self._are_records_stale_for_cmdr(cmdr_id):
            try:
                records = self.server.legal_stats(cmdr_id)
                now = datetime.datetime.now()
                self.records.set(cmdr_id, {"last_updated": now, "records": records})
                updated = True
            except Exception as e:
                EDR_LOG.exception(f"Failed to fetch/update records for {cmdr_id} - {e}")

        return updated

    def _process(self, legal_stats):
        """
        Process raw legal stats into a digestable format for the UI.

        Args:
            legal_stats (dict): stats by month.

        Returns:
            tuple: (clean_list, wanted_list, bounties_list, recent_stats_dict)
        """
        last = self._empty_monthly_bag()
        clean = []
        wanted = []
        bounties = []
        recent_stats = {"clean": 0, "wanted": 0, "maxBounty": 0, "last": {"value": 0, "timestamp": None, "starSystem": None}}
        now_date = datetime.datetime.now()
        current_year = now_date.year
        current_month = now_date.month
        orderly = self._orderly_month_no()
        month_span = int(min(12, round(1 + (self.timespan / (60 * 60 * 24) - now_date.day) / 30)))

        for m in orderly:
            if m not in legal_stats:
                clean.append(0)
                wanted.append(0)
                bounties.append(0)
                continue

            year = int(legal_stats[m]["year"])
            way_too_old = year < current_year - 1
            too_old = (year == current_year - 1) and int(m) <= current_month

            if way_too_old or too_old:
                clean.append(0)
                wanted.append(0)
                bounties.append(0)
                continue

            if m in orderly[12 - month_span:]:
                recent_stats["clean"] += legal_stats[m]["clean"]
                recent_stats["wanted"] += legal_stats[m]["wanted"]
                if legal_stats[m]["max"]:
                    recent_stats["maxBounty"] = max(recent_stats["maxBounty"], legal_stats[m]["max"].get("value", 0))
                if legal_stats[m]["last"] and legal_stats[m]["last"].get("value", 0) >= recent_stats["last"]["value"]:
                    recent_stats["last"] = legal_stats[m]["last"]

            clean.append(legal_stats[m]["clean"])
            wanted.append(legal_stats[m]["wanted"])
            last[m] = legal_stats[m]["last"]
            bounties.append(legal_stats[m]["max"]["value"])

        return clean, wanted, bounties, recent_stats

    @staticmethod
    def _orderly_month_no():
        """
        Return a list of month numbers string ordered from 11 months ago to now.

        Returns:
            list[str]: ordered month numbers (e.g. ['5', '6', ..., '4']).
        """
        current_month_idx0 = datetime.datetime.now().month - 1
        return [str((((current_month_idx0 - i) % 12) + 12) % 12) for i in range(11, -1, -1)]

    @staticmethod
    def _empty_monthly_bag():
        """
        Return a dictionary representing empty stats for each month index.

        Returns:
            dict: Keys '0'..'11', all None.
        """
        return {
            '0': None, '1': None, '2': None, '3': None, '4': None, '5': None,
            '6': None, '7': None, '8': None, '9': None, '10': None, '11': None
        }
