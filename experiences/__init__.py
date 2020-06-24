import importlib
import pkgutil
import os

from core.experience import Experience

pkg_dir = os.path.dirname(__file__)
for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):
    importlib.import_module('.' + name, __package__)

EXPERIENCES = {cls.NAME: cls for cls in Experience.__subclasses__()}