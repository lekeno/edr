import requests
import zipfile
import os
import json
import datetime

class EDRAutoUpdater(object):
    REPO = "lekeno/edr"
    LATEST = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'updates/latest.zip')
    BACKUP = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'backup/')
    EDR_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))

    def __init__(self):
        self.output = EDRAutoUpdater.LATEST

    def download_latest(self):
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
        files =  sorted(os.listdir(EDRAutoUpdater.BACKUP), key = os.path.getctime)
        nbfiles = len(files)
        max_backups = 5
        for i in range(0, nbfiles - max_backups):
            os.unlink(f)
            EDRLog.log(u"Removed backup {}".format(f), "INFO")

    def make_backup(self):
        name = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.zip'
        backup_file = EDRAutoUpdater.BACKUP + name
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
        with zipfile.ZipFile(EDRAutoUpdater.LATEST, "r") as latest:
            latest.extractall(EDRAutoUpdater.EDR_PATH)

    def __latest_release_url(self):
        latest_release_api = "https://api.github.com/repos/{}/releases/latest".format(self.REPO)
        response = requests.get(latest_release_api)
        if response.status_code != requests.codes.ok:
            #TODO error log
            return None
        json_resp = json.loads(response.content)
        assets = json_resp.get("assets", None)
        if not assets:
            return None
        return assets[0].get("browser_download_url", None)

