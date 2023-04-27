import os

from ..api import APIClient
from .resource import Collection, Model


class DSC(Model):
    """
    DSC info.
    """

    def __repr__(self):
        return "<{}: '({}) - {} - {}'>".format(
            self.__class__.__name__,
            self.magic,
            self.platform,
            self.uuid,
        )

    @property
    def magic(self):
        """
        The header magic.
        """
        return self.attrs["info"].get("magic", None)

    @property
    def uuid(self):
        """
        The header UUID.
        """
        return self.attrs["info"].get("uuid", None)

    @property
    def platform(self):
        """
        The header platform.
        """
        return self.attrs["info"].get("platform", None)

    @property
    def dylibs(self):
        """
        The DSC info.
        """
        return self.attrs["info"].get("dylibs", None)

    @property
    def info(self):
        """
        The DSC info.
        """
        return self.attrs.get("info", None)

    @property
    def path(self):
        """
        The DSC path.
        """
        return self.attrs.get("path", None)

    def a2o(self, addr=0):
        """
        Convert address to offsest.
        """
        return self.client.api.dsc_a2o(self.path, addr)

    def a2s(self, addrs=None, decode=False):
        """
        Lookup symbols for addresses.
        """
        return self.client.api.dsc_a2s(self.path, addrs, decode)

    def o2a(self, off=0):
        """
        Convert offsest to address.
        """
        return self.client.api.dsc_o2a(self.path, off)

    def dylib(self, dylib=None):
        """
        Get DSC dylib info.
        """
        return Dylib(
            image_name=dylib,
            attrs=self.client.api.dsc_macho(self.path, dylib),
            client=self.client,
            collection=self,
        )

    def sym_addrs(self, lookups=None):
        """
        Lookup symbols addresses.
        """
        return self.client.api.dsc_sym_addrs(self.path, lookups)

    def slide_infos(self, auth=False, decode=False):
        """
        Get DSC slide info.
        """
        return self.client.api.dsc_slide_info(self.path, auth, decode)


class Dylib(Model):
    """
    Dylib info.
    """

    def __init__(self, image_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.image_name = image_name

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
        return self.attrs["macho"]["header"].get("magic", None)

    @property
    def cpu(self):
        """
        The header CPU.
        """
        return self.attrs["macho"]["header"].get("cpu", None)

    @property
    def sub_cpu(self):
        """
        The header sub CPU.
        """
        return self.attrs["macho"]["header"].get("subcpu", None)

    @property
    def header(self):
        """
        The header.
        """
        return self.attrs["macho"].get("header", None)

    @property
    def load_commands(self):
        """
        The header.
        """
        return self.attrs["macho"].get("loads", None)


class Rebase(Model):
    """
    Rebase info.
    """

    def __repr__(self):
        return "<{}: '{}'>".format(
            self.__class__.__name__,
            self.pointer,
        )

    @property
    def pointer(self):
        """
        The rebase pointer.
        """
        return self.attrs.get("pointer", None)


class DscCollection(Collection):
    model = DSC

    def open(self, path=None):
        """
        Get DSC info.
        """
        return self.prepare_model(self.client.api.dsc_info(path))
