
import requests
import zipfile
import errno
import os
import datetime
import shutil
from .edrlog import EDR_LOG  # EDR_INTERNAL
from edr.utils.edrpath import plugin_root # EDR_INTERNAL


class EDRAutoUpdater:
    """
    Handles the automatic update process for EDR, including downloading the latest release,
    backing up the current version, and extracting the new version.
    """
    REPO = "lekeno/edr"
    EDR_PATH = plugin_root()
    UPDATES = os.path.join(EDR_PATH, 'updates')
    LATEST = os.path.join(EDR_PATH, 'updates', 'latest.zip')
    BACKUP = os.path.join(EDR_PATH, 'backup')
 
    OBSOLETE_ROOT_FILES = [
        "RESTFirebase.py",
        "__init__.py",
        "audiofeedback.py",
        "backoff.py",
        "clippy.py",
        "comparable.py",
        "edarmour.py",
        "edcargo.py",
        "edcargoreader.py",
        "edcodex.py",
        "edengineers.py",
        "edentities.py",
        "edinstance.py",
        "edmarketreader.py",
        "edmodule.py",
        "edmodulesinforeader.py",
        "edrafkdetector.py",
        "edrautoupdater.py",
        "edrbodiesofinterest.py",
        "edrbountyhuntingstats.py",
        "edrclient.py",
        "edrclientui.py",
        "edrcmdrprofile.py",
        "edrcmdrs.py",
        "edrcommands.py",
        "edrconfig.py",
        "edrdiscord.py",
        "edreconbox.py",
        "edrfactions.py",
        "edrfleet.py",
        "edrfleetcarrier.py",
        "edrfssinsights.py",
        "edrhitppoints.py",
        "edrhttpcache.py",
        "edri18n.py",
        "edrinventory.py",
        "edrlandables.py",
        "edrlegalrecords.py",
        "edrlog.py",
        "edrmarket.py",
        "edrminingstats.py",
        "edropponents.py",
        "edropsec.py",
        "edrparkingsystemfinder.py",
        "edrplanetfinder.py",
        "edrrawdepletables.py",
        "edrrealtime.py",
        "edrresourcefinder.py",
        "edrroutes.py",
        "edrserver.py",
        "edrservicecheck.py",
        "edrservicefinder.py",
        "edrsettlementfinder.py",
        "edrstatecheck.py",
        "edrstatefinder.py",
        "edrsysplacheck.py",
        "edrsyssetlcheck.py",
        "edrsysstacheck.py",
        "edrsystems.py",
        "edrtogglingpanel.py",
        "edrutils.py",
        "edrxzibit.py",
        "edshield.py",
        "edsitu.py",
        "edsmserver.py",
        "edspacesuits.py",
        "edtime.py",
        "edvehicles.py",
        "edweapons.py",
        "helpcontent.py",
        "igmconfig.py",
        "ingamemsg.py",
        "lrucache.py",
        "randomtips.py",
        "sseclient.py",
        "utils2to3.py",
    ]


    def __init__(self):
        """
        Initialize the EDRAutoUpdater.
        Setup paths for updates and backups.
        """
        self.updates = EDRAutoUpdater.UPDATES
        self.output = EDRAutoUpdater.LATEST

    def download_latest(self):
        """
        Downloads the latest release zip from GitHub.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.exists(self.updates):
            try:
                os.makedirs(self.updates)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    return False

        download_url = self.__latest_release_url()
        if not download_url:
            return False

        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            return False

        if response.status_code != requests.codes.ok:
            return False

        with open(self.output, 'wb') as handle:
            for block in response.iter_content(32768):
                handle.write(block)
        return True

    def clean_old_backups(self):
        """
        Removes old backups, keeping only the 5 most recent ones.
        """
        if not os.path.exists(EDRAutoUpdater.BACKUP):
            return

        files = os.listdir(EDRAutoUpdater.BACKUP)
        files = [os.path.join(EDRAutoUpdater.BACKUP, f) for f in files]
        files.sort(key=lambda x: os.path.getctime(x))
        nbfiles = len(files)
        max_backups = 5
        for i in range(0, nbfiles - max_backups):
            f = files[i]
            EDR_LOG.info(f"Removing backup {f}")
            try:
                os.unlink(f)
            except OSError as e:
                EDR_LOG.warning(f"Could not remove backup {f}: {e}")

    def make_backup(self):
        """
        Creates a zip backup of the current EDR installation.

        Returns:
            bool: True if successful, False otherwise.
        """
        if not os.path.exists(EDRAutoUpdater.BACKUP):
            try:
                os.makedirs(EDRAutoUpdater.BACKUP)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    return False

        name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.zip'
        backup_file = os.path.join(EDRAutoUpdater.BACKUP, name)

        try:
            zipf = zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED)
            self.__zipdir(EDRAutoUpdater.EDR_PATH, zipf)
            zipf.close()
            return True
        except Exception as e:
            EDR_LOG.error(f"Failed to create backup: {e}")
            return False

    def __zipdir(self, path, ziph):
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if (("updates" not in d) and ("backup" not in d))]
            for file in files:
                if file.endswith(".pyc") or file.endswith(".pyo"):
                    continue
                fp = os.path.join(root, file)
                ziph.write(fp, os.path.relpath(fp, EDRAutoUpdater.EDR_PATH))

    def extract_latest(self):
        """
        Extracts the latest update zip over the current installation.
        Handles new package structure detection and cleanup of obsolete files.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with zipfile.ZipFile(self.output, "r") as latest:
                file_names = latest.namelist()
                # Check if the zip contains the new package marker
                is_new_structure = any("edr/__init__.py" in f for f in file_names)

                if is_new_structure:
                    EDR_LOG.info("New package structure detected. Starting surgical cleanup.")
                    EDRAutoUpdater.clean_up_obsolete_files(self.EDR_PATH)

                    # 2. Clean up __pycache__
                    pycache_path = os.path.join(self.EDR_PATH, "__pycache__")
                    if os.path.exists(pycache_path):
                        try:
                            # ignore_errors=True is the 'nuclear' option for locked folders
                            shutil.rmtree(pycache_path, ignore_errors=True)
                            EDR_LOG.info("Cleaned up __pycache__")
                        except Exception as e:
                            EDR_LOG.warning(f"Cleanup: couldn't clear __pycache__: {e}")

                # Extract the new files.
                # If it's the new structure, it will create the 'edr/' folder.
                latest.extractall(self.EDR_PATH)
                EDR_LOG.info("Update extraction complete.")
                return True
        except Exception as e:
            EDR_LOG.error(f"Failed to extract update: {e}")
            return False

    @staticmethod
    def clean_up_obsolete_files(edr_path=None):
        """
        Removes known legacy files from the plugin root.
        """
        if edr_path is None:
            edr_path = EDRAutoUpdater.EDR_PATH
        for filename in EDRAutoUpdater.OBSOLETE_ROOT_FILES:
            fp = os.path.join(edr_path, filename)
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                    EDR_LOG.info(f"Cleaned up legacy file: {filename}")
                except (OSError, PermissionError) as e:
                    EDR_LOG.warning(f"Could not remove {filename}: {e}")

    def __latest_release_url(self):
        """
        Retrieves the download URL for the latest release from GitHub API.

        Returns:
            str: Download URL or None.
        """
        latest_release_api = "https://api.github.com/repos/{}/releases/latest".format(self.REPO)
        try:
            response = requests.get(latest_release_api)
            if response.status_code != requests.codes.ok:
                EDR_LOG.warning(f"Couldn't check the latest release on github: {response.status_code}")
                return None

            json_resp = response.json()
            assets = json_resp.get("assets", None)
            if not assets:
                return None
            return assets[0].get("browser_download_url", None)
        except Exception as e:
            EDR_LOG.warning(f"Error checking for updates: {e}")
            return None



