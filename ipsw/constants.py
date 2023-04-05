import sys
from .version import __version__

DEFAULT_IPSW_API_VERSION = '1.0'
MINIMUM_IPSW_API_VERSION = '1.0'
DEFAULT_TIMEOUT_SECONDS = 60
STREAM_HEADER_SIZE_BYTES = 8

DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_UNIX_SOCKET = "http+unix:///var/run/ipsw.sock"
DEFAULT_NPIPE = 'npipe:////./pipe/ipsw'

BYTE_UNITS = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
    'g': 1024 * 1024 * 1024
}

IS_WINDOWS_PLATFORM = (sys.platform == 'win32')
WINDOWS_LONGPATH_PREFIX = '\\\\?\\'

DEFAULT_USER_AGENT = f"ipsw-sdk-python/{__version__}"
DEFAULT_NUM_POOLS = 25

# The OpenSSH server default value for MaxSessions is 10 which means we can
# use up to 9, leaving the final session for the underlying SSH connection.
DEFAULT_NUM_POOLS_SSH = 9

DEFAULT_MAX_POOL_SIZE = 10

DEFAULT_DATA_CHUNK_SIZE = 1024 * 2048
