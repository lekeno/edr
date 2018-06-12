import requests
import zipfile
import os
import json

#TODO separate thread
class EDRAutoUpdater(object):
    REPO = "lekeno/edr"
    LATEST = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'updates/latest.zip')
    EDR_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)))

    def __init__(self):
        self.output = EDRAutoUpdater.LATEST

    def download_latest(self):
        download_url = self.__latest_release_url()
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        if response.status_code != requests.codes.ok:
            return False

        with open(self.output, 'wb') as handle:
            for block in response.iter_content(8192):
                handle.write(block)
        return True
    
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

