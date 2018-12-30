import os
import logging

from baseadmin.pki                     import decode

from baseadmin.backend.store           import setup, StoreNotAvailableError
from baseadmin.backend.store.provision import provision

class BackendError(Exception):
  pass

db          = None
private_key = None
public_key  = None

def init(provided_db=None):
  global db, private_key, public_key
  if not db is None: return

  try:
    db = provided_db or setup()
  except StoreNotAvailableError as e:
    raise BackendError("Could not initialize store: {0}".format(str(e)))

  # by default provisioning is only run once for each collection
  # setting a PROVISION environment variable forces re-provisioning
  force = not os.environ.get("BACKEND_PROVISION") is None
  provision(db, force)

  keys = db.pki.find_one({"_id": ""})

  private_key = decode(str(keys["key"]))
  public_key  = decode(str(keys["public"]))
