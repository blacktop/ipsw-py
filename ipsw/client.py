class IpswClient:
    """
    A client for communicating with an `ipsw` server.
    """
    def __init__(self, *args, **kwargs):
        self.api = None