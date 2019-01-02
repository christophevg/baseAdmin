__version__ = "1.0.0"

import os

from baseadmin import config

config["name"]        = "baseAdmin demo"
config["root"]        = os.path.dirname(__file__)
config["author"]      = "Christophe VG"
config["description"] = "A demo app for baseAdmin"
