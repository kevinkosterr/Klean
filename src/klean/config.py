import tomllib
from pathlib import Path

CONFIG_FOLDER = Path("~/.config/klean").expanduser()
CONFIG_FOLDER.mkdir(exist_ok=True)

CONFIG_PATH = CONFIG_FOLDER / "config.toml"
CONFIG_PATH.touch(exist_ok=True)


def get_config() -> dict:
    """Load the configuration file."""
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)
