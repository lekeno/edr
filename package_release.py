import os
import shutil
import json
import zipfile
import urllib.request
import re
from datetime import datetime

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
EDR_DIR = os.path.join(PROJECT_ROOT, 'edr')
BUILD_DIR = os.path.join(PROJECT_ROOT, '_build')
ASSETS_DIR = os.path.join(PROJECT_ROOT, '_build_assets')
CONFIG_JSON = os.path.join(PROJECT_ROOT, 'EDRecon.json')
CONFIG_INI = os.path.join(EDR_DIR, 'config', 'config.ini')
HISTORY_JSON = os.path.join(PROJECT_ROOT, 'release_history.json')
ENV_FILE = os.path.join(PROJECT_ROOT, '.env')

def int_to_roman(num):
    val = [10, 9, 5, 4, 1]
    syb = ["X", "IX", "V", "IV", "I"]
    roman_num = ""
    i = 0
    while num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num

def roman_to_int(s):
    roman = {'I': 1, 'V': 5, 'X': 10}
    res = 0
    for i in range(len(s)):
        if i > 0 and roman[s[i]] > roman[s[i - 1]]:
            res += roman[s[i]] - 2 * roman[s[i - 1]]
        else:
            res += roman[s[i]]
    return res

def increment_codename(codename):
    # Check if the codename ends with a Roman numeral
    match = re.search(r' (X|IX|V|IV|I+)$', codename)
    if match:
        roman = match.group(1)
        num = roman_to_int(roman)
        base = codename[:match.start()]
        return f"{base} {int_to_roman(num + 1)}"
    else:
        return f"{codename} II"

def load_history():
    if os.path.exists(HISTORY_JSON):
        try:
            with open(HISTORY_JSON, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load history: {e}")
    return {}

def save_history(version, codename, features):
    history = load_history()
    history[version] = {
        "codename": codename,
        "features": features,
        "timestamp": datetime.now().isoformat()
    }
    try:
        with open(HISTORY_JSON, 'w') as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

def get_suggested_release_info(version, history):
    # Exact match
    if version in history:
        return history[version].get("codename"), history[version].get("features", [])
    
    # Attempt to find a base version for incrementing (e.g., 3.3.1 -> 3.3.0)
    v_parts = version.split('.')
    if len(v_parts) >= 3:
        # Try decrementing the patch version
        try:
            patch = int(v_parts[-1])
            if patch > 0:
                prev_v = ".".join(v_parts[:-1] + [str(patch - 1)])
                if prev_v in history:
                    prev_codename = history[prev_v].get("codename")
                    if prev_codename:
                        return increment_codename(prev_codename), []
            else:
                # Try decrementing the minor version (e.g., 3.4.0 -> 3.3.something)
                minor = int(v_parts[1])
                if minor > 0:
                    base_minor = ".".join(v_parts[:2])
                    # Look for the latest patch in the previous minor
                    prev_minor_v = ".".join([v_parts[0], str(minor - 1)])
                    potential_matches = [v for v in history.keys() if v.startswith(prev_minor_v)]
                    if potential_matches:
                        latest_prev = sorted(potential_matches)[-1]
                        prev_codename = history[latest_prev].get("codename")
                        if prev_codename:
                            return increment_codename(prev_codename), []
        except ValueError:
            pass
    return None, []

def sync_to_fork():
    path = None
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            for line in f:
                if line.startswith('FORK_REPO_PATH='):
                    path = line.split('=')[1].strip()
                    break
    
    if not path:
        print("\nLocal fork path not configured.")
        path = input("Enter the absolute path to your local EDMC plugin repo fork: ").strip()
        if path:
            with open(ENV_FILE, 'a') as f:
                f.write(f"\nFORK_REPO_PATH={path}\n")
    
    if path and os.path.exists(path):
        try:
            target = os.path.join(path, 'EDRecon.json')
            shutil.copy2(CONFIG_JSON, target)
            print(f"Successfully synced EDRecon.json to {target}")
        except Exception as e:
            print(f"Error syncing to fork: {e}")
    elif path:
        print(f"Warning: Fork path '{path}' does not exist. Skipping sync.")

def get_current_version():
    with open(CONFIG_JSON, 'r') as f:
        data = json.load(f)
        return data.get('pluginVer', '0.0.0')

def get_latest_edmc_version():
    print("Fetching latest EDMC version from GitHub...")
    try:
        url = "https://github.com/EDCD/EDMarketConnector/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            final_url = response.geturl()
            # The URL will be like https://github.com/EDCD/EDMarketConnector/releases/tag/Release/6.1.2
            match = re.search(r'tag/Release/(\d+\.\d+\.\d+)', final_url)
            if match:
                return match.group(1)
            # Alternative format
            match = re.search(r'tag/(\d+\.\d+\.\d+)', final_url)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Warning: Could not fetch latest EDMC version: {e}")
    return None

def update_metadata(version, edmc_version=None):
    print(f"Updating metadata in EDRecon.json and config.ini to version {version}...")
    
    # Update EDRecon.json
    with open(CONFIG_JSON, 'r') as f:
        data = json.load(f)
    
    data['pluginVer'] = version
    data['pluginLastUpdate'] = datetime.now().strftime('%Y-%m-%d')
    if edmc_version:
        print(f"Updating pluginLastTestedEDMC to {edmc_version}...")
        data['pluginLastTestedEDMC'] = edmc_version
    
    with open(CONFIG_JSON, 'w') as f:
        json.dump(data, f, indent=2)

    # Update config.ini
    if os.path.exists(CONFIG_INI):
        with open(CONFIG_INI, 'r') as f:
            lines = f.readlines()
        
        with open(CONFIG_INI, 'w') as f:
            for line in lines:
                if line.startswith('version ='):
                    f.write(f"version = {version}\n")
                else:
                    f.write(line)
    else:
        print(f"Warning: {CONFIG_INI} not found. Skipping version update in .ini file.")

def create_build_structure(version, codename):
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR)
    os.makedirs(BUILD_DIR)

    # Folders that need a dummy file
    dummy_folders = ['backup', 'cache', 'db', 'private', 'updates']
    for folder in dummy_folders:
        path = os.path.join(BUILD_DIR, folder)
        os.makedirs(path)
        with open(os.path.join(path, 'dummy'), 'w') as f:
            f.write('')

    # Copy standard folders from edr/
    folders_to_copy = ['config', 'data', 'l10n', 'sounds', 'src']
    for folder in folders_to_copy:
        src = os.path.join(EDR_DIR, folder)
        dst = os.path.join(BUILD_DIR, folder)
        if os.path.exists(src):
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '.vscode', '*.pyc', '.ropeproject'))
        else:
            print(f"Warning: Folder {folder} not found in edr/")

    # Extra for sounds: ensure sounds/custom exists
    custom_sounds = os.path.join(BUILD_DIR, 'sounds', 'custom')
    if not os.path.exists(custom_sounds):
        os.makedirs(custom_sounds)

    # Copy root files
    shutil.copy2(os.path.join(EDR_DIR, 'load.py'), BUILD_DIR)
    shutil.copy2(os.path.join(EDR_DIR, 'readme.txt'), BUILD_DIR)

    # External Assets (EDMCOverlay)
    overlay_src = os.path.join(ASSETS_DIR, 'EDMCOverlay')
    if os.path.exists(overlay_src):
        shutil.copytree(overlay_src, os.path.join(BUILD_DIR, 'EDMCOverlay'))
    else:
        print(f"Warning: EDMCOverlay not found in {ASSETS_DIR}. Please ensure it is present.")

    # Manuals (Renaming from underscores to spaces as per release process)
    manuals = {
        'english/ED_Recon_-_The_Missing_Manual.pdf': 'ED Recon - The Missing Manual.pdf',
        'français/ED_Recon_-_Le_Guide.pdf': 'ED Recon - Le Guide.pdf',
        'italiano/ED_Recon_-_Il_Manuale_Mancante.pdf': 'ED Recon - Il Manuale Mancante.pdf'
    }
    
    for src_rel, dst_name in manuals.items():
        src_path = os.path.join(EDR_DIR, 'docs', src_rel)
        if os.path.exists(src_path):
            shutil.copy2(src_path, os.path.join(BUILD_DIR, dst_name))
        else:
            print(f"Warning: Manual {src_rel} not found in edr/docs/")

def create_zip(version, is_rc=False):
    suffix = " RC" if is_rc else ""
    zip_name = f"EDRv{version}{suffix}.zip"
    zip_path = os.path.join(PROJECT_ROOT, zip_name)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(BUILD_DIR):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, BUILD_DIR)
                zipf.write(file_path, arcname)
    
    print(f"Release package created: {zip_path}")
    return zip_name

def generate_comms(version, codename, features):
    print("Generating communication templates...")
    
    discord = f"**EDR v{version} \"{codename}\" released**\n"
    for f in features:
        discord += f" - {f}\n"
    discord += " - Misc fixes and improvements."

    motd = {
        "autoupdatable": True,
        "l10n_motd": {
            "default": [codename, ", ".join(features)],
            "fr": [codename, "Mise à jour pour " + version]
        },
        "latest": version,
        "min": version
    }

    forum = f"[center][b][size=6]ED Recon (EDR) v{version} \"{codename}\" released[/size][/b][/center]\n\n"
    forum += "Greetings Commanders! A new version of EDR is now available.\n\n**Key Changes:**\n"
    for f in features:
        forum += f"- {f}\n"
    forum += "\nYou can download the latest version from GitHub: https://github.com/lekeno/edr/releases/latest"

    with open(os.path.join(PROJECT_ROOT, 'release_notes.txt'), 'w', encoding='utf-8') as f:
        f.write("=== DISCORD / GITHUB RELEASE NOTES ===\n")
        f.write(discord + "\n\n")
        f.write("=== SERVER BACKEND MOTD (JSON) ===\n")
        f.write(json.dumps(motd, indent=2, ensure_ascii=False) + "\n\n")
        f.write("=== FORUM POST ===\n")
        f.write(forum + "\n")
    
    print("Communication templates saved to release_notes.txt")

def main():
    current_ver = get_current_version()
    print(f"Current version is: {current_ver}")
    
    new_ver = input(f"Enter version number [{current_ver}]: ").strip() or current_ver
    is_rc = input("Is this a Release Candidate? (y/n) [n]: ").strip().lower() == 'y'
    
    history = load_history()
    suggested_codename, suggested_features = get_suggested_release_info(new_ver, history)
    
    codename_prompt = f"Enter release codename [{suggested_codename}]: " if suggested_codename else "Enter release codename (e.g. Witty Narwhal): "
    codename = input(codename_prompt).strip() or suggested_codename or "Unnamed"
    
    edmc_ver = get_latest_edmc_version()
    if edmc_ver:
        print(f"Detected latest EDMC version: {edmc_ver}")
        use_edmc = input(f"Update folder json with this EDMC version? (y/n) [y]: ").strip().lower() != 'n'
        if not use_edmc:
            edmc_ver = None
    
    if suggested_features:
        print(f"Found existing features for version {new_ver}:")
        for f in suggested_features:
            print(f" - {f}")
        use_features = input("Reuse these features? (y/n) [y]: ").strip().lower() != 'n'
        if use_features:
            features = suggested_features
        else:
            suggested_features = []

    if not suggested_features:
        print("Enter key features (one per line, empty line to finish):")
        features = []
        while True:
            line = input("> ").strip()
            if not line:
                break
            features.append(line)

    if not is_rc:
        update_metadata(new_ver, edmc_ver)
        save_history(new_ver, codename, features)
        sync_to_fork()
    
    create_build_structure(new_ver, codename)
    create_zip(new_ver, is_rc)
    generate_comms(new_ver, codename, features)
    
    print("\nRelease process completed!")
    if not is_rc:
        print("Don't forget to push your changes and tag the release on GitHub.")

if __name__ == "__main__":
    main()
