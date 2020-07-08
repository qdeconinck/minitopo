import importlib
import pkgutil
import os

from core.experiment import Experiment

pkg_dir = os.path.dirname(__file__)
for (module_loader, name, ispkg) in pkgutil.iter_modules([pkg_dir]):
    importlib.import_module('.' + name, __package__)

# Track indirect inheritance
EXPERIMENTS = {}

def _get_all_subclasses(BaseClass):
    for cls in BaseClass.__subclasses__():
        if hasattr(cls, "NAME"):
            EXPERIMENTS[cls.NAME] = cls
        
        _get_all_subclasses(cls)

_get_all_subclasses(Experiment)