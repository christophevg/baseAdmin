import logging
logger = logging.getLogger(__name__)

import uuid

from baseadmin.storage import db

from baseadmin.backend.repositories import clients

def get():
  return [ file for file in db.files.find({"path": { "$exists" : True }} ) ]
