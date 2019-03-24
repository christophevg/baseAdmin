from baseadmin.storage import db

def register(request):
  try:
    db.requests.insert_one({
      "name"  : request["name"],
      "pass"  : request["pass"],
      "pubkey": request["pubkey"]
    })
  except KeyError as e:
    raise ValueError("invalid request: {0}".format(str(e)))
