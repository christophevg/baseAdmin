import logging
logger = logging.getLogger(__name__)

import uuid

from flask         import request, Response
from flask_restful import Resource

from baseadmin.backend.api.rest            import api
from baseadmin.backend.security            import authenticated
from baseadmin.backend.repositories.tokens import browser

class Session(Resource):
  @authenticated("users")
  def get(self):
    try:
      logger.info("providing new session token to browser...")
      return browser.renew()
    except Exception as e:
      logger.exception("failed to  provide session")
      return Response("failed to provide session", 500)

api.add_resource(Session, "/api/session")
