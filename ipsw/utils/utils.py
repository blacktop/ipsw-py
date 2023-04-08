import collections
import os
import string

from .. import errors
from ..constants import DEFAULT_HTTP_HOST
from ..constants import DEFAULT_UNIX_SOCKET
from ..constants import DEFAULT_NPIPE
from ..constants import BYTE_UNITS

from urllib.parse import urlparse, urlunparse
from packaging.version import Version

URLComponents = collections.namedtuple(
    "URLComponents",
    "scheme netloc url params query fragment",
)


def parse_host(addr, is_win32=False, tls=False):
    # Sensible defaults
    if not addr and is_win32:
        return DEFAULT_NPIPE
    if not addr or addr.strip() == "unix://":
        return DEFAULT_UNIX_SOCKET

    addr = addr.strip()

    parsed_url = urlparse(addr)
    proto = parsed_url.scheme
    if not proto or any([x not in string.ascii_letters + "+" for x in proto]):
        # https://bugs.python.org/issue754016
        parsed_url = urlparse("//" + addr, "tcp")
        proto = "tcp"

    if proto == "fd":
        raise errors.IpswException("fd protocol is not implemented")

    # These protos are valid aliases for our library but not for the
    # official spec
    if proto == "http" or proto == "https":
        tls = proto == "https"
        proto = "tcp"
    elif proto == "http+unix":
        proto = "unix"

    if proto not in ("tcp", "unix", "npipe", "ssh"):
        raise errors.IpswException(f"Invalid bind address protocol: {addr}")

    if proto == "tcp" and not parsed_url.netloc:
        # "tcp://" is exceptionally disallowed by convention;
        # omitting a hostname for other protocols is fine
        raise errors.IpswException(f"Invalid bind address format: {addr}")

    if any([parsed_url.params, parsed_url.query, parsed_url.fragment, parsed_url.password]):
        raise errors.IpswException(f"Invalid bind address format: {addr}")

    if parsed_url.path and proto == "ssh":
        raise errors.IpswException("Invalid bind address format: no path allowed for this protocol:" " {}".format(addr))
    else:
        path = parsed_url.path
        if proto == "unix" and parsed_url.hostname is not None:
            # For legacy reasons, we consider unix://path
            # to be valid and equivalent to unix:///path
            path = "/".join((parsed_url.hostname, path))

    netloc = parsed_url.netloc
    if proto in ("tcp", "ssh"):
        port = parsed_url.port or 0
        if port <= 0:
            if proto != "ssh":
                raise errors.IpswException("Invalid bind address format: port is required:" " {}".format(addr))
            port = 22
            netloc = f"{parsed_url.netloc}:{port}"

        if not parsed_url.hostname:
            netloc = f"{DEFAULT_HTTP_HOST}:{port}"

    # Rewrite schemes to fit library internals (requests adapters)
    if proto == "tcp":
        proto = "http{}".format("s" if tls else "")
    elif proto == "unix":
        proto = "http+unix"

    if proto in ("http+unix", "npipe"):
        return f"{proto}://{path}".rstrip("/")

    return urlunparse(
        URLComponents(
            scheme=proto,
            netloc=netloc,
            url=path,
            params="",
            query="",
            fragment="",
        )
    ).rstrip("/")


def kwargs_from_env(ssl_version=None, assert_hostname=None, environment=None):
    if not environment:
        environment = os.environ
    host = environment.get("IPSW_HOST")

    # empty string for cert path is the same as unset.
    cert_path = environment.get("IPSW_CERT_PATH") or None

    # empty string for tls verify counts as "false".
    # Any value or 'unset' counts as true.
    tls_verify = environment.get("IPSW_TLS_VERIFY")
    if tls_verify == "":
        tls_verify = False
    else:
        tls_verify = tls_verify is not None
    enable_tls = cert_path or tls_verify

    params = {}

    if host:
        params["base_url"] = host

    if not enable_tls:
        return params

    if not cert_path:
        cert_path = os.path.join(os.path.expanduser("~"), ".config", "ipsw")

    if not tls_verify and assert_hostname is None:
        # assert_hostname is a subset of TLS verification,
        # so if it's not set already then set it to false.
        assert_hostname = False

    # params['tls'] = TLSConfig(
    #     client_cert=(os.path.join(cert_path, 'cert.pem'),
    #                  os.path.join(cert_path, 'key.pem')),
    #     ca_cert=os.path.join(cert_path, 'ca.pem'),
    #     verify=tls_verify,
    #     ssl_version=ssl_version,
    #     assert_hostname=assert_hostname,
    # )

    return params


def format_environment(environment):
    def format_env(key, value):
        if value is None:
            return key
        if isinstance(value, bytes):
            value = value.decode("utf-8")

        return f"{key}={value}"

    return [format_env(*var) for var in iter(environment.items())]


def compare_version(v1, v2):
    """Compare docker versions

    >>> v1 = '1.9'
    >>> v2 = '1.10'
    >>> compare_version(v1, v2)
    1
    >>> compare_version(v2, v1)
    -1
    >>> compare_version(v2, v2)
    0
    """
    s1 = Version(v1)
    s2 = Version(v2)
    if s1 == s2:
        return 0
    elif s1 > s2:
        return -1
    else:
        return 1


def version_lt(v1, v2):
    return compare_version(v1, v2) > 0


def version_gte(v1, v2):
    return not version_lt(v1, v2)
