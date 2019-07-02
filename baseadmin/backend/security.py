import logging
logger = logging.getLogger(__name__)

from functools import wraps

import bcrypt

from flask import request, Response

from baseadmin         import config
from baseadmin.storage import db

def valid_credentials(group):
  auth = request.authorization
  if not auth or not auth.username or not auth.password:
    logger.debug("no authentication information for {0}".format(request.full_path))
    return False
  user = db[group].find_one({ "_id" : auth.username })
  if not user:
    logger.debug("unknown {0} member: {1}".format(group, auth.username))
    return False
  if not bcrypt.hashpw(auth.password, user["pass"]) == user["pass"]:
    logger.debug("incorrect password")
    return False
  return True

def authenticated(group):
  def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      if not valid_credentials(group):
        return Response( "", 401,
          { 'WWW-Authenticate': 'Basic realm="' + config.app.name + '"' }
        )
      return f(*args, **kwargs)
    return wrapper
  return decorator
