__version__ = "1.0.0"

import os
import logging

from baseadmin.backend.web import server
from baseadmin.backend     import config

config["name"]        = "baseAdmin demo"
config["root"]        = os.path.dirname(__file__)
config["author"]      = "Christophe VG"
config["description"] = "A demo app for baseAdmin"

