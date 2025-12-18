
import requests
import zipfile
import errno
import os
import json
import datetime
from edrlog import EDR_LOG # EDR_INTERNAL




class EDRAutoUpdater(object):
    REPO = "lekeno/edr"
    UPDATES = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'updates')
    LATEST = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'updates', 'latest.zip')
    BACKUP = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backup')
    EDR_PATH = os.path.abspath(os.path.dirname(__file__))

    def __init__(self):
        self.updates = EDRAutoUpdater.UPDATES
        self.output = EDRAutoUpdater.LATEST
        

    def download_latest(self):
        if not os.path.exists(self.updates):
            try:
                os.makedirs(self.updates)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    return False

        download_url = self.__latest_release_url()
        if not download_url:
            return False
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        if response.status_code != requests.codes.ok:
            return False

        with open(self.output, 'wb') as handle:
            for block in response.iter_content(32768):
                handle.write(block)
        return True

    def clean_old_backups(self):
        files = os.listdir(EDRAutoUpdater.BACKUP)
        files = [os.path.join(EDRAutoUpdater.BACKUP, f) for f in files]
        files.sort(key=lambda x: os.path.getctime(x))
        nbfiles = len(files)
        max_backups = 5
        for i in range(0, nbfiles - max_backups):
            f = files[i]
            EDR_LOG.info("Removing backup {}".format(f))
            os.unlink(f)

    def make_backup(self):
        if not os.path.exists(EDRAutoUpdater.BACKUP):
            try:
                os.makedirs(EDRAutoUpdater.BACKUP)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    return False
        name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.zip'
        backup_file = os.path.join(EDRAutoUpdater.BACKUP, name)
        zipf = zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED)
        self.__zipdir(EDRAutoUpdater.EDR_PATH, zipf)
        zipf.close()

    def __zipdir(self, path, ziph):
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if (("updates" not in d) and ("backup" not in d))]
            for file in files:
                if file.endswith(".pyc") or file.endswith(".pyo"):
                    continue
                fp = os.path.join(root, file)
                ziph.write(fp, os.path.relpath(fp, EDRAutoUpdater.EDR_PATH))

    def extract_latest(self):
        with zipfile.ZipFile(self.output, "r") as latest:
            file_names = latest.namelist()
            # Check if the zip contains the new package marker
            is_new_structure = any("edr/__init__.py" in f for f in file_names)
            
            if is_new_structure:
                EDR_LOG.info("New package structure detected. Starting surgical cleanup.")
                for filename in self.OBSOLETE_ROOT_FILES:
                    fp = os.path.join(self.EDR_PATH, filename)
                    if os.path.exists(fp):
                        try:
                            os.remove(fp)
                            EDR_LOG.info(f"Cleaned up legacy file: {filename}")
                        except (OSError, PermissionError) as e:
                            EDR_LOG.warning(f"Could not remove {filename}: {e}")

                # 2. Clean up __pycache__
                pycache_path = os.path.join(self.EDR_PATH, "__pycache__")
                if os.path.exists(pycache_path):
                    try:
                        import shutil
                        # ignore_errors=True is the 'nuclear' option for locked folders
                        shutil.rmtree(pycache_path, ignore_errors=True)
                        EDR_LOG.info("Cleaned up __pycache__")
                    except Exception as e:
                        EDR_LOG.warning(f"Cleanup: couldn't clear __pycache__: {e}")

            # Extract the new files. 
            # If it's the new structure, it will create the 'edr/' folder.
            latest.extractall(self.EDR_PATH)
            EDR_LOG.info("Update extraction complete.")

    def __latest_release_url(self):
        latest_release_api = "https://api.github.com/repos/{}/releases/latest".format(self.REPO)
        response = requests.get(latest_release_api)
        if response.status_code != requests.codes.ok:
            EDR_LOG.warning(f"Couldn't check the latest release on github: {response.status_code}")
            return None
        json_resp = json.loads(response.content)
        assets = json_resp.get("assets", None)
        if not assets:
            return None
        return assets[0].get("browser_download_url", None)

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
    ]


