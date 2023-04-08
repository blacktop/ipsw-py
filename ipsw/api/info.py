class InfoApiMixin:
    def ipsw_info(self, path=None):
        """
        Display IPSW information. Identical to the ``ipsw info``
        command.

        Returns:
            (dict): The info as a dict

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._get(self._url("/info/ipsw"), params={"path": path}), True)

    def ota_info(self, path=None):
        """
        Display OTA information. Identical to the ``ipsw info``
        command.

        Returns:
            (dict): The info as a dict

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._get(self._url("/info/ota"), params={"path": path}), True)

    def remote_ipsw_info(self, url=None, proxy=None, insecure=False):
        """
        Display remote IPSW information. Identical to the ``ipsw info --remote``
        command.

        Returns:
            (dict): The info as a dict

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._get(self._url("/info/ipsw/remote"), params={url, proxy, insecure}), True)

    def remote_ota_info(self, url=None, proxy=None, insecure=False):
        """
        Display remote OTA information. Identical to the ``ipsw info --remote``
        command.

        Returns:
            (dict): The info as a dict

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._get(self._url("/info/ota/remote"), params={url, proxy, insecure}), True)
