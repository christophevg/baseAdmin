import logging

import simple_rsa as rsa

from baseadmin import storage

class KeyStore(object):
  def __init__(self):
    self.private, self.public = self[""]
    if self.private is None:
      self.provision()

  def __getitem__(self, name):
    logging.debug("load keys for {0}".format(name))
    keys = storage.db.pki.find_one({"_id": name})
    try:
      return ( rsa.decode(str(keys["key"])), rsa.decode(str(keys["public"])) )
    except Exception as e:
      logging.warn(str(e))
      return ( None, None )

  def provision(self):
    self.private, self.public = rsa.generate_key_pair()
    storage.provision(
      "pki",
      [
        {
          "_id"    : "",
          "key"    : rsa.encode(self.private),
          "public" : rsa.encode(self.public)
        }
      ]
    )

keys = None

def init():
  global keys
  storage.init()
  keys = KeyStore()
