import logging
logger = logging.getLogger(__name__)

import os

from baseadmin.backend.interface import register_component
from baseadmin.backend.socketio  import command, current_client, socketio

register_component("Download.js", os.path.dirname(__file__))

@command("newFile")
def on_new_file(feedback):
  client = current_client()
  with client.lock:
    logger.warn("newFile: {0} : {1} => {2}".format(client.name, client.state, feedback["state"]))
    client.state = feedback["state"]
    socketio.emit("newfile", dict(client), room="browser" )
