import logging
logger = logging.getLogger(__name__)

import os

from os import listdir
from os.path import isfile, join

from flask          import request
from flask_restful  import Resource, abort
from werkzeug.utils import secure_filename

from baseadmin.backend.api.rest  import api
from baseadmin.backend.security  import authenticated
from baseadmin.backend.socketio  import register_state_provider
from baseadmin.backend.interface import register_component
from baseadmin.backend.socketio  import command

register_component("MasterUpload.js", os.path.dirname(__file__))

ROOT = os.environ.get("FILES_UPLOAD_ROOT")
if not ROOT: ROOT = "files/"

def list_files():
  files = []
  try:
    for fname in listdir(ROOT):
      file = join(ROOT, fname)
      if isfile(file):
        files.append({
          "name" : fname,
          "size" : os.stat(file).st_size
        })
  except OSError as e:
    logger.error("can't access files @ " + ROOT + ": " + str(e))
  return files

# send current content on connect
register_state_provider("files", list_files)

# accept new content => send content update

class FileServer(Resource):
  @authenticated("users")
  def post(self):
    file = request.files['filename']
    if file:
      filename = secure_filename(file.filename)
      local_file = os.path.join(ROOT, filename)
      logger.info("savind new uploaded file: {0}".format(filename))
      file.save(local_file)
      return { "name" : filename, "size" : os.stat(local_file).st_size }
    return False

api.add_resource(FileServer,
  "/api/content"
)

# allow removal of files
@command("removeFile")
def on_remove(file):
  logger.debug("removing " + file)
  local_file = os.path.join(ROOT, file)
  if not isfile(local_file):
    raise KeyError("unknown file {0}".format(file))
  os.remove(local_file)
