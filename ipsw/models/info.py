import os

from ..api import APIClient
from .resource import Collection, Model


class Info(Model):
    """
    IPSW/OTA info.
    """

    def __repr__(self):
        return "<{}: '{} ({})'>".format(
            self.__class__.__name__,
            self.version,
            self.build,
        )

    @property
    def version(self):
        """
        The iOS version.
        """
        return self.attrs["info"]["Plists"]["restore"].get("ProductVersion", None)

    @property
    def build(self):
        """
        The iOS version.
        """
        return self.attrs["info"]["Plists"]["restore"].get("ProductBuildVersion", None)

    @property
    def devices(self):
        """
        The iOS devices.
        """
        devices = set()
        for dt in self.attrs["info"]["DeviceTrees"].values():
            for child in dt["device-tree"]["children"]:
                if "product" in child:
                    devices.add(child["product"]["product-name"])
        devlist = list(devices)
        devlist.sort()
        return devlist


class InfoCollection(Collection):
    model = Info

    def get(self, ipsw=None, ota=None, url=None):
        """
        The iOS version.
        """
        if url:
            return self.prepare_model(self.client.api.remote_ipsw_info(url))
        else:
            if ipsw:
                return self.prepare_model(self.client.api.ipsw_info(os.path.abspath(ipsw)))
            elif ota:
                return self.prepare_model(self.client.api.ipsw_info(os.path.abspath(ipsw)))
