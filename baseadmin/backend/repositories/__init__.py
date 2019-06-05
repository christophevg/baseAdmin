from baseadmin.storage import db
from baseadmin.backend.repositories.client import Clients
from baseadmin.backend.repositories.group  import Groups

clients = Clients(db.clients)
groups  = Groups(db.groups)
