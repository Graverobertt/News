import json
import os
import requests
from datetime import datetime

REMOTE_JSON_URL = "https://raw.githubusercontent.com/Graverobertt/News/refs/heads/main/Version.json"   # <-- replace with your Drive/GitHub link
LOCAL_LICENSE_FILE = "license_key.txt"
CURRENT_VERSION = "1.0.0"

def compare_versions(v1, v2):
    """Return True if v1 >= v2."""
    a = [int(x) for x in v1.split(".")]
    b = [int(x) for x in v2.split(".")]
    return a >= b


def load_remote_config():
    """Fetch Version.json from remote and return as dict."""
    try:
        r = requests.get(REMOTE_JSON_URL, timeout=5)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[SECURITY] Could not fetch remote config: {e}")
        return None


def check_license(valid_keys):
    """Checks/asks for a license key and stores it locally."""
    # If already stored, validate it
    if os.path.exists(LOCAL_LICENSE_FILE):
        saved = open(LOCAL_LICENSE_FILE, "r").read().strip()
        if saved in valid_keys:
            print("[LICENCE] Existing license accepted.")
            return True
        else:
            print("[LICENCE] Saved license is invalid.")

    # Ask user for a key
    key = input("Enter your license key: ").strip()
    if key in valid_keys:
        with open(LOCAL_LICENSE_FILE, "w") as f:
            f.write(key)
        print("[LICENCE] License accepted and saved.")
        return True

    print("[LICENCE] Invalid license. Exiting...")
    return False


def security_check():
    """Main security validation (license + forced update)."""
    print("[SECURITY] Checking remote configuration...")

    remote = load_remote_config()
    if not remote:
        print("[SECURITY] Could not validate remote config. Exiting for safety.")
        return False

    valid_keys = remote.get("valid_keys", [])
    mandatory_update = remote.get("mandatory_update", True)
    latest_version = remote.get("latest_version", CURRENT_VERSION)
    min_version = remote.get("min_version", CURRENT_VERSION)

    # 1. LICENSE CHECK ---------------------------------------------------------
    if not check_license(valid_keys):
        return False

    # 2. VERSION / UPDATE CHECK ------------------------------------------------
    # If the version is below min_version → force exit
    if not compare_versions(CURRENT_VERSION, min_version):
        print("\n***************************************")
        print("  Your version is too old and must be updated.")
        print("***************************************\n")
        return False

    # If update is mandatory and newer version exists
    if mandatory_update and not compare_versions(CURRENT_VERSION, latest_version):
        print("\n***************************************")
        print("  A mandatory update is required.")
        print("***************************************\n")
        return False

    print("[SECURITY] Security + License OK.")
    return True
