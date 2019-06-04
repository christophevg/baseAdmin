import logging
logger = logging.getLogger(__name__)

import sys

from baseadmin.storage  import db
from baseadmin.endpoint import register, run, command, me, socketio

# example "bulky" state update command

@command("update")
def on_update(state):
  logger.info("updating state")
  me.state = state

# example background reporting thread
def report():
  while True:
    if me.connected:
      socketio.emit("report", "hello from {0}".format(me.name))
    socketio.sleep(300)

socketio.start_background_task(report)



master = db.config.find_one({"_id": "master"})
if master: master = master["value"]

try:
  if not master:
    if not register():
      logger.fatal("registration was rejected, can't continue.")
      sys.exit(1)
  run()
except KeyboardInterrupt:
  pass
