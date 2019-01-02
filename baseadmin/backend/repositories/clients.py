import baseadmin

def register(request):
  try:
    baseadmin.db.requests.insert_one({
      "name"      : request["name"],
      "pass"      : request["pass"],
      "pubkey"    : request["pubkey"]
    })
  except KeyError:
    raise ValueError("invalid request")
