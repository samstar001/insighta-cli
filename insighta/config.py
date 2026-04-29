import json
import os
from pathlib import Path
from typing import Optional

# ~/.insighta/ folder — works on Windows, Mac, Linux
CREDENTIALS_DIR = Path.home() / ".insighta"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"

# Your deployed backend URL
DEFAULT_API_URL = os.getenv(
    "INSIGHTA_API_URL",
    "https://profile-intelligence-service-rcl7.vercel.app"
)


def get_api_url() -> str:
    """Returns the backend API base URL."""
    return DEFAULT_API_URL


def save_credentials(
    access_token: str,
    refresh_token: str,
    username: str,
    role: str
) -> None:
    """
    Saves tokens and user info to ~/.insighta/credentials.json
    Creates the directory if it doesn't exist.
    """
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    # parents=True — creates parent dirs if needed
    # exist_ok=True — doesn't error if dir already exists

    credentials = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "username": username,
        "role": role,
    }

    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(credentials, f, indent=2)


def load_credentials() -> Optional[dict]:
    """
    Loads credentials from ~/.insighta/credentials.json
    Returns None if file doesn't exist or is invalid.
    """
    if not CREDENTIALS_FILE.exists():
        return None

    try:
        with open(CREDENTIALS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None


def clear_credentials() -> None:
    """Deletes the credentials file (logout)."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()
        # .unlink() = delete the file


def is_logged_in() -> bool:
    """Returns True if credentials file exists with tokens."""
    creds = load_credentials()
    return creds is not None and bool(creds.get("access_token"))