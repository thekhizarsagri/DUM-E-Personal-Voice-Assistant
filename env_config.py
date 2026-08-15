import os
from pathlib import Path


def load_env():
    """Load variables from a .env file next to this script into os.environ."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def get_api_key(name: str) -> str:
    """Return an API key from env, or an empty string if missing."""
    return os.environ.get(name, "").strip()