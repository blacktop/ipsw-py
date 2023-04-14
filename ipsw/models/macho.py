import os

from ..api import APIClient
from .resource import Collection, Model


class Macho(Model):
    """
    MachO info.
    """

    def __repr__(self):
        return "<{}: '{} {} ({})'>".format(
            self.__class__.__name__,
            self.magic,
            self.cpu,
            self.sub_cpu,
        )

    @property
    def magic(self):
        """
        The header magic.
        """
        return self.attrs["info"]["header"].get("magic", None)

    @property
    def cpu(self):
        """
        The header CPU.
        """
        return self.attrs["info"]["header"].get("cpu", None)

    @property
    def sub_cpu(self):
        """
        The header sub CPU.
        """
        return self.attrs["info"]["header"].get("subcpu", None)

    @property
    def header(self):
        """
        The header.
        """
        return self.attrs["info"].get("header", None)


class MachoCollection(Collection):
    model = Macho

    def get(self, path=None, arch=None):
        """
        Get MachO info.
        """
        return self.prepare_model(self.client.api.macho_info(path, arch))
