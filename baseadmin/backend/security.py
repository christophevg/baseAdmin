import logging
from functools import wraps

import bcrypt

from flask import request, Response

from baseadmin         import config
from baseadmin.storage import db

def valid_credentials(group, auth):
  logging.debug("checking authentication for {0}".format(group))
  if not auth or not auth.username or not auth.password:
    logging.debug("non authentication information")
    return False
  user = db[group].find_one({ "_id" : auth.username })
  if not user:
    logging.debug("unknown {0} member: {1}".format(group, auth.username))
    return False
  if not bcrypt.checkpw(auth.password, user["pass"]):
    logging.debug("incorrect password")
    return False
  return True

def authenticated(group):
  def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      if not valid_credentials(group, request.authorization):
        return Response( "", 401,
          { 'WWW-Authenticate': 'Basic realm="' + config.app.name + '"' }
        )
      return f(*args, **kwargs)
    return wrapper
  return decorator
