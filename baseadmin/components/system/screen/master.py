import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.backend.interface import register_component
from baseadmin.backend.socketio  import command

# add component UI

register_component("Screen.js", os.path.dirname(__file__))
