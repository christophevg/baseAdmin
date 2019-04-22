import logging

logger = logging.getLogger(__name__)

import simple_rsa as rsa

from baseadmin.storage import db

class KeyStore(object):
  def __init__(self):
    self._private = None
    self._public  = None
  
  @property
  def private(self):
    self.provision()
    return self._private
  
  @property
  def public(self):
    self.provision()
    return self._public

  def __getitem__(self, name):
    self.provision()
    if name == "":
      private, public = self._private, self._public
    else:
      private, public = self.load(name)
    return {
      "private" : private,
      "public"  : public
    }

  def load(self, name=""):
    logger.debug("load keys for '{0}'".format(name))
    keys = db.pki.find_one({"_id": name})
    try:
      return (rsa.decode(str(keys["private"])), rsa.decode(str(keys["public"])))
    except Exception as e:
      logger.error(str(e))
      return None

  def provision(self):
    if not self._private is None: return
    if db.pki.count_documents({}) > 0:
      logger.info("loading own keys")
      self._private, self._public = self.load()
    else:
      logger.info("generating own keys")
      self._private, self._public = rsa.generate_key_pair()
      db.provision(
        "pki",
        [
          {
            "_id"    : "",
            "private": rsa.encode(self._private),
            "public" : rsa.encode(self._public)
          }
        ]
      )

keys = KeyStore()
