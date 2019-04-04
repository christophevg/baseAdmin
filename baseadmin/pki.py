import logging

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
    logging.debug("load keys for {0}".format(name))
    keys = db.pki.find_one({"_id": name})
    try:
      return  {
        "private": rsa.decode(str(keys["private"])),
        "public" : rsa.decode(str(keys["public"]))
      }
    except Exception as e:
      logging.warn(str(e))
      return None

  def provision(self):
    if db.pki.count_documents({}) > 0: return
    logging.info("provisioning  PKI")
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
