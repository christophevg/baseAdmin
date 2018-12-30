from baseadmin.backend import db

def register(request):
  try:
    db.requests.insert_one({
      "name"      : request["name"],
      "pass"      : request["pass"],
      "pubkey"    : request["pubkey"]
    })
  except KeyError:
    raise ValueError("invalid request")
