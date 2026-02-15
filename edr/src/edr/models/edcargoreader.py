import json
from os.path import join
from config import config
from edr.core.edrlog import EDR_LOG  # EDR_INTERNAL


class EDCargoReader:
    """
    Reads the Cargo.json file from the journal directory.
    """

    def __init__(self):
        """Initialize the reader with the journal location."""
        self.journal_location = config.get_str('journaldir') or config.default_journal_dir

    def process(self):
        """Read and parse the Cargo.json file.

        Returns:
            dict: The parsed JSON data as a dictionary, or None if failed.
        """
        # From EDMarketConnector while waiting for first party support
        try:
            with open(join(self.journal_location, 'Cargo.json'), 'rb') as handle:
                data = handle.read().strip()
                if data:  # Can be empty if polling while the file is being re-written
                    entry = json.loads(data)
                    return entry
        except Exception:
            EDR_LOG.exception("Couldn't process cargo")
            return None
