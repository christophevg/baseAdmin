import os
import logging
import bcrypt

from baseadmin     import config
from baseadmin.pki import generate_key_pair, encode

# provision initial users collection

def load(db, collection, data, force=False):
  if force or not collection in db.list_collection_names():
    logging.info("provisioning " + collection)
    if force:
      logging.info("dropping existing collection: " + collection)
      db[collection].drop();
    logging.info("provisioning collection: " + collection)
    db[collection].insert_many(data)

def provision_users(db, force=False):
  load(
    db,
    "users",
    [
      {
        "_id"     : "admin",
        "name"    : "Admin",
        "password": bcrypt.hashpw(config["admin"]["pass"], bcrypt.gensalt())
      },
      {
        "_id"     : config["register"]["user"],
        "name"    : "Client Registration Account",
        "password": bcrypt.hashpw(config["register"]["pass"], bcrypt.gensalt())
      },
    ],
    force
  )

def provision_pki(db, force=False):
  key, public = generate_key_pair()
  load(
    db,
    "pki",
    [
      {
        "_id"    : "",
        "key"    : encode(key),
        "public" : encode(public)
      }
    ],
    force
  )

def provision(db, force=False):
  provision_users(db, force)
  provision_pki(db, force)
