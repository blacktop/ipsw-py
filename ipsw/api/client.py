import json
import struct
import urllib
from functools import partial

import requests
import requests.exceptions
import websocket

from ..constants import (
    DEFAULT_MAX_POOL_SIZE,
    DEFAULT_NUM_POOLS,
    DEFAULT_NUM_POOLS_SSH,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_USER_AGENT,
    IS_WINDOWS_PLATFORM,
    MINIMUM_IPSW_API_VERSION,
    STREAM_HEADER_SIZE_BYTES,
)
from ..errors import InvalidVersion, IpswException, create_api_error_from_http_exception
from ..transport import UnixHTTPAdapter
from ..utils import config, update_headers, utils
from ..utils.json_stream import json_stream
from ..utils.proxy import ProxyConfig
from ..utils.socket import consume_socket_output, demux_adaptor, frames_iter
from .daemon import DaemonApiMixin
from .dsc import DscApiMixin
from .info import InfoApiMixin
from .macho import MachoApiMixin

try:
    from ..transport import NpipeHTTPAdapter
except ImportError:
    pass

try:
    from ..transport import SSHHTTPAdapter
except ImportError:
    pass


class APIClient(requests.Session, DaemonApiMixin, DscApiMixin, InfoApiMixin, MachoApiMixin):
    """
    A low-level client for the ipsw API.

    Example:

        >>> import ipsw
        >>> client = ipsw.APIClient(base_url='unix://var/run/ipsw.sock')
        >>> client.version()
        {u'ApiVersion': u'1.0',
         u'Arch': u'amd64',
         u'BuildTime': u'2017-11-19T18:46:37.000000000+00:00',
         u'GitCommit': u'f4ffd2511c',
         u'GoVersion': u'go1.9.2',
         u'MinAPIVersion': u'1.0',
         u'Os': u'linux'}

    Args:
        base_url (str): URL to the ipsw server. For example,
            ``unix:///var/run/ipsw.sock`` or ``tcp://127.0.0.1:1234``.
        version (str): The version of the API to use. Set to ``auto`` to
            automatically detect the server's version. Default: ``1.35``
        timeout (int): Default timeout for API calls, in seconds.
        user_agent (str): Set a custom user agent for requests to the server.
        use_ssh_client (bool): If set to `True`, an ssh connection is made
            via shelling out to the ssh client. Ensure the ssh client is
            installed and configured on the host.
        max_pool_size (int): The maximum number of connections
            to save in the pool.
    """

    __attrs__ = requests.Session.__attrs__ + ["_general_configs", "_version", "base_url", "timeout"]

    def __init__(
        self,
        base_url=None,
        version=None,
        timeout=DEFAULT_TIMEOUT_SECONDS,
        user_agent=DEFAULT_USER_AGENT,
        num_pools=None,
        use_ssh_client=False,
        max_pool_size=DEFAULT_MAX_POOL_SIZE,
    ):
        super().__init__()

        self.base_url = base_url
        self.timeout = timeout
        self.headers["User-Agent"] = user_agent

        self._general_configs = config.load_general_config()

        proxy_config = self._general_configs.get("proxies", {})
        try:
            proxies = proxy_config[base_url]
        except KeyError:
            proxies = proxy_config.get("default", {})

        self._proxy_configs = ProxyConfig.from_dict(proxies)

        base_url = utils.parse_host(
            base_url,
            IS_WINDOWS_PLATFORM,
        )
        # SSH has a different default for num_pools to all other adapters
        num_pools = num_pools or DEFAULT_NUM_POOLS_SSH if base_url.startswith("ssh://") else DEFAULT_NUM_POOLS

        if base_url.startswith("http+unix://"):
            self._custom_adapter = UnixHTTPAdapter(
                base_url, timeout, pool_connections=num_pools, max_pool_size=max_pool_size
            )
            self.mount("http+ipsw://", self._custom_adapter)
            self._unmount("http://", "https://")
            # host part of URL should be unused, but is resolved by requests
            # module in proxy_bypass_macosx_sysconf()
            self.base_url = "http+ipsw://localhost"
        elif base_url.startswith("npipe://"):
            if not IS_WINDOWS_PLATFORM:
                raise IpswException("The npipe:// protocol is only supported on Windows")
            try:
                self._custom_adapter = NpipeHTTPAdapter(
                    base_url, timeout, pool_connections=num_pools, max_pool_size=max_pool_size
                )
            except NameError:
                raise IpswException("Install pypiwin32 package to enable npipe:// support")
            self.mount("http+ipsw://", self._custom_adapter)
            self.base_url = "http+ipsw://localnpipe"
        elif base_url.startswith("ssh://"):
            try:
                self._custom_adapter = SSHHTTPAdapter(
                    base_url, timeout, pool_connections=num_pools, max_pool_size=max_pool_size, shell_out=use_ssh_client
                )
            except NameError:
                raise IpswException("Install paramiko package to enable ssh:// support")
            self.mount("http+ipsw://ssh", self._custom_adapter)
            self._unmount("http://", "https://")
            self.base_url = "http+ipsw://ssh"
        else:
            self.base_url = base_url

        # version detection needs to be after unix adapter mounting
        if version is None or (isinstance(version, str) and version.lower() == "auto"):
            self._version = self._retrieve_server_version()
        else:
            self._version = version
        if not isinstance(self._version, str):
            raise IpswException("Version parameter must be a string or None. Found {}".format(type(version).__name__))
        if utils.version_lt(self._version, MINIMUM_IPSW_API_VERSION):
            raise InvalidVersion(
                "API versions below {} are no longer supported by this " "library.".format(MINIMUM_IPSW_API_VERSION)
            )

    def _retrieve_server_version(self):
        try:
            return self.version(api_version=False)["api_version"]
        except KeyError:
            raise IpswException('Invalid response from ipsw daemon: key "api_version"' " is missing.")
        except Exception as e:
            raise IpswException(f"Error while fetching server API version: {e}")

    def _set_request_timeout(self, kwargs):
        """Prepare the kwargs for an HTTP request by inserting the timeout
        parameter, if not already present."""
        kwargs.setdefault("timeout", self.timeout)
        return kwargs

    @update_headers
    def _post(self, url, **kwargs):
        return self.post(url, **self._set_request_timeout(kwargs))

    @update_headers
    def _get(self, url, **kwargs):
        return self.get(url, **self._set_request_timeout(kwargs))

    @update_headers
    def _put(self, url, **kwargs):
        return self.put(url, **self._set_request_timeout(kwargs))

    @update_headers
    def _delete(self, url, **kwargs):
        return self.delete(url, **self._set_request_timeout(kwargs))

    def _url(self, pathfmt, *args, **kwargs):
        for arg in args:
            if not isinstance(arg, str):
                raise ValueError("Expected a string but found {} ({}) " "instead".format(arg, type(arg)))

        quote_f = partial(urllib.parse.quote, safe="/:")
        args = map(quote_f, args)

        if kwargs.get("versioned_api", True):
            return "{}/v{}{}".format(self.base_url, self._version, pathfmt.format(*args))
        else:
            return f"{self.base_url}{pathfmt.format(*args)}"

    def _raise_for_status(self, response):
        """Raises stored :class:`APIError`, if one occurred."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise create_api_error_from_http_exception(e) from e

    def _result(self, response, json=False, binary=False):
        assert not (json and binary)
        self._raise_for_status(response)

        if json:
            return response.json()
        if binary:
            return response.content
        return response.text

    def _post_json(self, url, data, **kwargs):
        # Go <1.1 can't unserialize null to a string
        # so we do this disgusting thing here.
        data2 = {}
        if data is not None and isinstance(data, dict):
            for k, v in iter(data.items()):
                if v is not None:
                    data2[k] = v
        elif data is not None:
            data2 = data

        if "headers" not in kwargs:
            kwargs["headers"] = {}
        kwargs["headers"]["Content-Type"] = "application/json"
        return self._post(url, data=json.dumps(data2), **kwargs)

    def _attach_params(self, override=None):
        return override or {"stdout": 1, "stderr": 1, "stream": 1}

    def _create_websocket_connection(self, url):
        return websocket.create_connection(url)

    def _get_raw_response_socket(self, response):
        self._raise_for_status(response)
        if self.base_url == "http+ipsw://localnpipe":
            sock = response.raw._fp.fp.raw.sock
        elif self.base_url.startswith("http+ipsw://ssh"):
            sock = response.raw._fp.fp.channel
        else:
            sock = response.raw._fp.fp.raw
            if self.base_url.startswith("https://"):
                sock = sock._sock
        try:
            # Keep a reference to the response to stop it being garbage
            # collected. If the response is garbage collected, it will
            # close TLS sockets.
            sock._response = response
        except AttributeError:
            # UNIX sockets can't have attributes set on them, but that's
            # fine because we won't be doing TLS over them
            pass

        return sock

    def _stream_helper(self, response, decode=False):
        """Generator for data coming from a chunked-encoded HTTP response."""

        if response.raw._fp.chunked:
            if decode:
                yield from json_stream(self._stream_helper(response, False))
            else:
                reader = response.raw
                while not reader.closed:
                    # this read call will block until we get a chunk
                    data = reader.read(1)
                    if not data:
                        break
                    if reader._fp.chunk_left:
                        data += reader.read(reader._fp.chunk_left)
                    yield data
        else:
            # Response isn't chunked, meaning we probably
            # encountered an error immediately
            yield self._result(response, json=decode)

    def _multiplexed_buffer_helper(self, response):
        """A generator of multiplexed data blocks read from a buffered
        response."""
        buf = self._result(response, binary=True)
        buf_length = len(buf)
        walker = 0
        while True:
            if buf_length - walker < STREAM_HEADER_SIZE_BYTES:
                break
            header = buf[walker : walker + STREAM_HEADER_SIZE_BYTES]
            _, length = struct.unpack_from(">BxxxL", header)
            start = walker + STREAM_HEADER_SIZE_BYTES
            end = start + length
            walker = end
            yield buf[start:end]

    def _multiplexed_response_stream_helper(self, response):
        """A generator of multiplexed data blocks coming from a response
        stream."""

        # Disable timeout on the underlying socket to prevent
        # Read timed out(s) for long running processes
        socket = self._get_raw_response_socket(response)
        self._disable_socket_timeout(socket)

        while True:
            header = response.raw.read(STREAM_HEADER_SIZE_BYTES)
            if not header:
                break
            _, length = struct.unpack(">BxxxL", header)
            if not length:
                continue
            data = response.raw.read(length)
            if not data:
                break
            yield data

    def _stream_raw_result(self, response, chunk_size=1, decode=True):
        """Stream result for TTY-enabled container and raw binary data"""
        self._raise_for_status(response)

        # Disable timeout on the underlying socket to prevent
        # Read timed out(s) for long running processes
        socket = self._get_raw_response_socket(response)
        self._disable_socket_timeout(socket)

        yield from response.iter_content(chunk_size, decode)

    def _read_from_socket(self, response, stream, tty=True, demux=False):
        """Consume all data from the socket, close the response and return the
        data. If stream=True, then a generator is returned instead and the
        caller is responsible for closing the response.
        """
        socket = self._get_raw_response_socket(response)

        gen = frames_iter(socket, tty)

        if demux:
            # The generator will output tuples (stdout, stderr)
            gen = (demux_adaptor(*frame) for frame in gen)
        else:
            # The generator will output strings
            gen = (data for (_, data) in gen)

        if stream:
            return gen
        else:
            try:
                # Wait for all frames, concatenate them, and return the result
                return consume_socket_output(gen, demux=demux)
            finally:
                response.close()

    def _disable_socket_timeout(self, socket):
        """Depending on the combination of python version and whether we're
        connecting over http or https, we might need to access _sock, which
        may or may not exist; or we may need to just settimeout on socket
        itself, which also may or may not have settimeout on it. To avoid
        missing the correct one, we try both.

        We also do not want to set the timeout if it is already disabled, as
        you run the risk of changing a socket that was non-blocking to
        blocking, for example when using gevent.
        """
        sockets = [socket, getattr(socket, "_sock", None)]

        for s in sockets:
            if not hasattr(s, "settimeout"):
                continue

            timeout = -1

            if hasattr(s, "gettimeout"):
                timeout = s.gettimeout()

            # Don't change the timeout if it is already disabled.
            if timeout is None or timeout == 0.0:
                continue

            s.settimeout(None)

    def _unmount(self, *args):
        for proto in args:
            self.adapters.pop(proto)

    def get_adapter(self, url):
        try:
            return super().get_adapter(url)
        except requests.exceptions.InvalidSchema as e:
            if self._custom_adapter:
                return self._custom_adapter
            else:
                raise e

    @property
    def api_version(self):
        return self._version
