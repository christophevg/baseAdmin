import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.backend.interface import register_component

register_component("ClientPing.js", os.path.dirname(__file__))
