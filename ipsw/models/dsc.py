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


class DscCollection(Collection):
    model = DSC

    def get_info(self, path=None):
        """
        Get DSC info.
        """
        return self.prepare_model(self.client.api.dsc_info(path))

    def get_dylib(self, path=None, dylib=None):
        """
        Get DSC dylib info.
        """
        return Dylib(
            image_name=dylib,
            attrs=self.client.api.dsc_macho(path, dylib),
            client=self.client,
            collection=self,
        )
