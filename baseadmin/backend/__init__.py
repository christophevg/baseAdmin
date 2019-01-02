import os
import logging
import bcrypt

import baseadmin
from baseadmin import config, store

# provision initial users collection

def init():
  provision_users(baseadmin.db)

def provision_users(db, force=False):
  store.load(
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
