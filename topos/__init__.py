import importlib
import pkgutil
import os

from core.topo import Topo, TopoConfig

pkg_dir = os.path.dirname(__file__)
for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):
    importlib.import_module('.' + name, __package__)

configs = {cls.NAME: cls for cls in TopoConfig.__subclasses__()}
topos = {cls.NAME: cls for cls in Topo.__subclasses__()}