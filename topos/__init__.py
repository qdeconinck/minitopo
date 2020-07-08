import importlib
import pkgutil
import os

from core.topo import Topo, TopoConfig

pkg_dir = os.path.dirname(__file__)
for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):
    importlib.import_module('.' + name, __package__)

# Track indirect inheritance
TOPO_CONFIGS = {}
TOPOS = {}

def _get_all_subclasses(BaseClass, dico):
    for cls in BaseClass.__subclasses__():
        if hasattr(cls, "NAME"):
            dico[cls.NAME] = cls

        _get_all_subclasses(cls, dico)

_get_all_subclasses(TopoConfig, TOPO_CONFIGS)
_get_all_subclasses(Topo, TOPOS)