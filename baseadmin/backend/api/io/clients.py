import logging
logger = logging.getLogger(__name__)

from baseadmin.backend.socketio     import socketio, secured
from baseadmin.backend.repositories import registration

@socketio.on("accept")
@secured
def accept(message):
  logger.info("accept: {0}".format(message))
  registration.accept(message["client"], message["master"] if "master" in message else None)
  return True
