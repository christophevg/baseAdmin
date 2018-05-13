import os
import logging
import bcrypt

from backend.web   import server
from backend.store import store

# provision initial users collection

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
if not ADMIN_PASSWORD:
  ADMIN_PASSWORD = "admin"

def provision(collection, data, force=False):
  if force or not collection in store.collection_names():
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

# provision initial app collection
def provision_app(force=False):
  provision(
    "app",
    {
      "name" : "baseAdmin Demo",
      "sections" : [
        {
          "name" : "dashboard",
          "label": "Dashboard"
        }
      ]
    },
    force
  )

# by default provisioning is only run once for each collection
# setting a PROVISION environment variable forces re-provisioning
force = not os.environ.get("PROVISION") is None
with server.app_context():
  provision_users(force)
  provision_app(force)
