import os
import logging
import bcrypt

from baseadmin.backend.web   import server
from baseadmin.backend.store import store

# provision initial users collection

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
  ADMIN_PASSWORD = "admin"

def provision(collection, data, force=False):
  if force or not collection in store.collection_names():
    logging.info("provisioning " + collection)
    if force:
      logging.info("dropping existing collection: " + collection)
      store[collection].drop();
    logging.info("provisioning collection: " + collection)
    store[collection].insert_one(data)

def provision_users(force=False):
  provision(
    "users",
    {
      "_id"     : "admin",
      "name"    : "Admin",
      "password": bcrypt.hashpw(ADMIN_PASSWORD, bcrypt.gensalt())
    },
    force
  )

# by default provisioning is only run once for each collection
# setting a PROVISION environment variable forces re-provisioning
force = not os.environ.get("BACKEND_PROVISION") is None
with server.app_context():
  provision_users(force)
