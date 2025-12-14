# VENI VIDI VICI
# BY ROBERTO LIZZA
# security_check.py

import json
import os
import time
import requests
import tkinter as tk
from tkinter import messagebox, simpledialog

# ------------------------------------------------------
# CONFIG
# ------------------------------------------------------

LICENSE_URL = "https://raw.githubusercontent.com/Graverobertt/News/refs/heads/main/Version.json"
REQUEST_TIMEOUT = 5

CACHE_MAX_AGE = 60 * 60 * 24 * 3  # 3 days
APP_NAME = "ImageDownloader"

CACHE_DIR = os.path.join(
    os.path.expanduser("~"),
    "Library",
    "Application Support",
    APP_NAME
)
CACHE_FILE = os.path.join(CACHE_DIR, "Version.json")

# ------------------------------------------------------
# PUBLIC API
# ------------------------------------------------------

def validate_license():
    """
    Main entry point.
    Returns True if app is allowed to run.
    """
    os.makedirs(CACHE_DIR, exist_ok=True)

    cached = _load_cache()

    # 1) Try remote first (authoritative)
    remote = _fetch_remote()

    if remote:
        if not remote.get("require_license", False):
            return True

        licenses = remote.get("licenses", {})

        # Determine license code
        license_code = cached.get("license") if cached else _ask_license()
        if not license_code:
            return False

        lic = licenses.get(license_code)

        if not lic:
            _error(
                "Invalid license",
                "This license key does not exist.\n\nPlease contact support."
            )
            return False

        if not lic.get("active", False):
            _error(
                "License disabled",
                "Your access has been disabled.\n\nPlease contact support."
            )
            return False

        # Success → refresh cache
        _write_cache(license_code)
        return True

    # 2) Remote failed → fallback to cache
    if cached and _cache_is_fresh(cached):
        return True

    _error(
        "License check failed",
        "Could not verify your license.\n\n"
        "Please connect to the internet."
    )
    return False

# ------------------------------------------------------
# INTERNALS
# ------------------------------------------------------

def _fetch_remote():
    try:
        url = LICENSE_URL + "?t=" + str(int(time.time()))
        r = requests.get(url, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def _ask_license():
    root = tk.Tk()
    root.withdraw()
    code = simpledialog.askstring(
        "License required",
        "Enter your license key:"
    )
    root.destroy()
    return code.strip() if code else None


def _write_cache(code):
    payload = {
        "license": code,
        "validated_at": int(time.time())
    }
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f)


def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _cache_is_fresh(data):
    ts = data.get("validated_at", 0)
    return (time.time() - ts) <= CACHE_MAX_AGE


def _error(title, msg):
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror(title, msg)
    root.destroy()
