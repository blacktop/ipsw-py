import yaml
import logging
import os

from ..constants import IS_WINDOWS_PLATFORM

IPSW_CONFIG_FILENAME = os.path.join('.config', 'ipsw', 'config.yml')

log = logging.getLogger(__name__)


def find_config_file(config_path=None):
    paths = list(filter(None, [
        config_path,  # 1
        config_path_from_environment(),  # 2
        os.path.join(home_dir(), IPSW_CONFIG_FILENAME),  # 3
    ]))

    log.debug(f"Trying paths: {repr(paths)}")

    for path in paths:
        if os.path.exists(path):
            log.debug(f"Found file at path: {path}")
            return path

    log.debug("No config file found")

    return None


def config_path_from_environment():
    config_dir = os.environ.get('IPSW_CONFIG')
    if not config_dir:
        return None
    return os.path.join(config_dir, os.path.basename(IPSW_CONFIG_FILENAME))


def home_dir():
    """
    Get the user's home directory, using the same logic as the ipsw
    client - use %USERPROFILE% on Windows, $HOME/getuid on POSIX.
    """
    if IS_WINDOWS_PLATFORM:
        return os.environ.get('USERPROFILE', '')
    else:
        return os.path.expanduser('~')


def load_general_config(config_path=None):
    config_file = find_config_file(config_path)

    if not config_file:
        return {}

    try:
        with open(config_file) as f:
            return yaml.safe_load(f)
    except (OSError, ValueError) as e:
        log.debug(e)

    log.debug("All parsing attempts failed - returning empty config")
    return {}