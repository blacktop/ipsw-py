class DscApiMixin:
    def dsc_a2o(self, path=None, addr=0):
        """
        Convert virtual address to offset. Identical to the ``ipsw dyld a2o``
        command.

        Args:
            path (str): The path to the dyld_shared_cache file.
            addr (int): The address to convert to an offset.

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._post_json(self._url("/dsc/a2o"), data={"path": path, "addr": addr}), True)

    def dsc_a2s(self, path=None, addrs=None, decode=False):
        """
        Lookup symbol for address. Identical to the ``ipsw dyld a2s``
        command.

        Args:
            path (str): The path to the dyld_shared_cache file.
            addrs ([int]): List of addresses of the symbols to lookup.
            decode (bool): If set to true, stream will be decoded into dicts
                on the fly. False by default.

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        params = {
            "path": path,
            "addrs": addrs,
        }
        url = self._url("/dsc/a2s")
        response = self._post_json(url, data=params, stream=True, timeout=None)
        return self._stream_helper(response, decode=decode)

    def dsc_o2a(self, path=None, off=0):
        """
        Convert offset to virtual address. Identical to the ``ipsw dyld o2a``
        command.

        Args:
            path (str): The path to the dyld_shared_cache file.
            off (int): The offset to convert to an address.

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._post_json(self._url("/dsc/o2a"), data={"path": path, "off": off}), True)

    def dsc_info(self, path=None):
        """
        Display DSC header information. Identical to the ``ipsw dyld info --dylibs --json``
        command.

        Returns:
            (dict): The info as a dict

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._get(self._url("/dsc/info"), params={"path": path}), True)

    def dsc_macho(self, path=None, dylib=None):
        """
        Display DSC dylib information. Identical to the ``ipsw dyld macho DSC DYLIB --json``
        command.

        Returns:
            (dict): The info as a dict

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._get(self._url("/dsc/macho"), params={"path": path, "dylib": dylib}), True)

    def dsc_sym_addrs(self, path=None, lookups=None):
        """
        Display DSC dylib slide info. Identical to the ``ipsw dyld slide``
        command.

        Args:
            path (str): The path to the dyld_shared_cache file.
            lookups (dict): Symbol lookups.

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._post_json(self._url("/dsc/symaddr"), data={"path": path, "lookups": lookups}), True)

    def dsc_slide_info(self, path=None, auth=False, decode=False):
        """
        Display DSC dylib slide info. Identical to the ``ipsw dyld slide``
        command.

        Args:
            path (str): The path to the dyld_shared_cache file.
            auth (bool): Filter to only ``auth`` slide-info. False by default.
            decode (bool): If set to true, stream will be decoded into dicts
                on the fly. False by default.

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        params = {
            "path": path,
            "type": "auth" if auth else "",
        }
        url = self._url("/dsc/slide")
        response = self._post_json(url, data=params, stream=True, timeout=None)
        return self._stream_helper(response, decode=decode)
