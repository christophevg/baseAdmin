from baseadmin.storage import db
from baseadmin.backend.repositories.client import Clients
clients = Clients(db.clients)
