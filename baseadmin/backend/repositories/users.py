import bcrypt

from baseadmin         import config
from baseadmin.storage import db

def count():
  return db.users.count()

def list():
  return [ user for user in db.users.find() ]

def get(id):
  return db.users.find_one({ "_id" :id })

def create(user):
  db.users.insert_one({
    "_id" : user["name"],
    "pass": bcrypt.hashpw(user["pass"], bcrypt.gensalt())
  })
