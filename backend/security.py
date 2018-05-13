from functools import wraps

import bcrypt

from flask import request, Response

from backend       import APP_NAME
from backend.store import store

def valid_credentials(users, auth):
  if not auth or not auth.username or not auth.password: return False
  if not auth.username in users: return False
  user = store.users.find_one({ "_id" : auth.username })
  if not user: return False
  return bcrypt.checkpw(auth.password, user["password"])

def authenticate(users):
  def decorator(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
      if not valid_credentials(users, request.authorization):
        return Response(
          '', 401, { 'WWW-Authenticate': 'Basic realm="' + APP_NAME + '"' }
        )
      return f(*args, **kwargs)
    return wrapper
  return decorator
