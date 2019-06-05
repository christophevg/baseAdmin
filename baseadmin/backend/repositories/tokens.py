import logging
logger = logging.getLogger(__name__)

import uuid

from baseadmin.storage import db

from baseadmin.backend.repositories import clients

class Browser(object):
  def __init__(self):
    try:
      self.token = db.config.find_one({"_id": "browser.token"})["token"]
      logger.info("loaded current browser token {0}".format(self.token))
    except:
      self.token = None
  
  def renew(self):
    self.token = str(uuid.uuid4())
    db.config.update_one(
      {"_id":  "browser.token"},
      { "$set":  { "token": self.token  }  },
      upsert=True
    )
    logger.info("renewed browser token {0}".format(self.token))
    return self.token

browser = Browser()

def get(name):
  if name == "browser":
    return browser.token
  else:
    if name in clients: return clients[name].token
    return None
