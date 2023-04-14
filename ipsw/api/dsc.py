class DscApiMixin:
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
