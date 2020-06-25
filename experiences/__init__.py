import importlib
import pkgutil
import os

from core.experience import Experience

pkg_dir = os.path.dirname(__file__)
for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):
    importlib.import_module('.' + name, __package__)

# Track direct inheritance
EXPERIENCES = {}

def _get_all_subclasses(BaseClass):
    for cls in BaseClass.__subclasses__():
        if hasattr(cls, "NAME"):
            EXPERIENCES[cls.NAME] = cls
        
        _get_all_subclasses(cls)

_get_all_subclasses(Experience)