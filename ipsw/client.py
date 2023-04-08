from .api.client import APIClient
from .constants import (DEFAULT_TIMEOUT_SECONDS, DEFAULT_MAX_POOL_SIZE)
from .models.info import InfoCollection
from .utils import kwargs_from_env


class IpswClient:
    """
    A client for communicating with a ipsw server.

    Example:

        >>> import ipsw
        >>> client = ipsw.IpswClient(base_url='unix://var/run/ipsw.sock')

    Args:
        base_url (str): URL to the ipsw server. For example,
            ``unix:///var/run/ipsw.sock`` or ``tcp://127.0.0.1:8080``.
        version (str): The version of the API to use. Set to ``auto`` to
            automatically detect the server's version. Default: ``1.0``
        timeout (int): Default timeout for API calls, in seconds.
        user_agent (str): Set a custom user agent for requests to the server.
        use_ssh_client (bool): If set to `True`, an ssh connection is made
            via shelling out to the ssh client. Ensure the ssh client is
            installed and configured on the host.
        max_pool_size (int): The maximum number of connections
            to save in the pool.
    """
    def __init__(self, *args, **kwargs):
        self.api = APIClient(*args, **kwargs)

    @classmethod
    def from_env(cls, **kwargs):
        """
        Return a client configured from environment variables.

        The environment variables used are the same as those used by the
        ipsw command-line client. They are:

        .. envvar:: IPSW_HOST

            The URL to the ipsw host.

        Args:
            version (str): The version of the API to use. Set to ``auto`` to
                automatically detect the server's version. Default: ``auto``
            timeout (int): Default timeout for API calls, in seconds.
            max_pool_size (int): The maximum number of connections
                to save in the pool.
            assert_hostname (bool): Verify the hostname of the server.
            environment (dict): The environment to read environment variables
                from. Default: the value of ``os.environ``
            use_ssh_client (bool): If set to `True`, an ssh connection is
                made via shelling out to the ssh client. Ensure the ssh
                client is installed and configured on the host.

        Example:

            >>> import ipsw
            >>> client = ipsw.from_env()
            
        """
        timeout = kwargs.pop('timeout', DEFAULT_TIMEOUT_SECONDS)
        max_pool_size = kwargs.pop('max_pool_size', DEFAULT_MAX_POOL_SIZE)
        version = kwargs.pop('version', None)
        use_ssh_client = kwargs.pop('use_ssh_client', False)
        return cls(
            timeout=timeout,
            max_pool_size=max_pool_size,
            version=version,
            use_ssh_client=use_ssh_client,
            **kwargs_from_env(**kwargs)
        )

    @property
    def info(self):
        """
        An object for getting local/remote IPSW/OTA info.
        """
        return InfoCollection(client=self)

    # Top-level methods
    def ping(self, *args, **kwargs):
        return self.api.ping(*args, **kwargs)
    ping.__doc__ = APIClient.ping.__doc__

    def version(self, *args, **kwargs):
        return self.api.version(*args, **kwargs)
    version.__doc__ = APIClient.version.__doc__

    def close(self):
        return self.api.close()
    close.__doc__ = APIClient.close.__doc__

    def __getattr__(self, name):
        s = [f"'IpswClient' object has no attribute '{name}'"]
        # If a user calls a method on APIClient, they
        if hasattr(APIClient, name):
            s.append("In ipsw SDK for Python 2.0, this method is now on the "
                     "object APIClient. See the low-level API section of the "
                     "documentation for more details.")
        raise AttributeError(' '.join(s))


from_env = IpswClient.from_env