import logging

import simple_rsa as rsa

from baseadmin.storage import db

class KeyStore(object):
  def __init__(self):
    self._private = None
    self._public  = None
  
  @property
  def private(self):
    self.lazy_init()
    return self._private
  
  @property
  def public(self):
    self.lazy_init()
    return self._public

  def lazy_init(self):
    if self._private is None: self.load()
    if self._private is None: self.provision()

  def load(self):
    self._private, self._public = self[""]

  def provision(self):
    self._private, self._public = rsa.generate_key_pair()
    db.provision(
      "pki",
      [
        {
          "_id"    : "",
          "private": rsa.encode(self.private),
          "public" : rsa.encode(self.public)
        }
      ]
    )

  def __getitem__(self, name):
    logging.debug("load keys for {0}".format(name))
    keys = db.pki.find_one({"_id": name})
    try:
      return ( rsa.decode(str(keys["private"])), rsa.decode(str(keys["public"])) )
    except Exception as e:
      logging.warn(str(e))
      return ( None, None )

keys = KeyStore()
