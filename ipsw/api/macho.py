class MachoApiMixin:
    def macho_info(self, path=None, arch=None):
        """
        Display MachO header information. Identical to the ``ipsw macho info --json``
        command.

        Returns:
            (dict): The info as a dict

        Raises:
            :py:class:`ipsw.errors.APIError`
                If the server returns an error.
        """
        return self._result(self._get(self._url("/macho/info"), params={"path": path, "arch": arch}), True)
