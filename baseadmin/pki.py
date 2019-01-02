import base64
import json

from cryptography.hazmat.backends import default_backend

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric import padding

def generate_key_pair():
  key = rsa.generate_private_key(
     public_exponent=65537,
     key_size=2048,
     backend=default_backend()
  )
  return key, key.public_key()

def encode(key):
  if isinstance(key, rsa.RSAPublicKey):
    return key.public_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
  else:
    return key.private_bytes(
      encoding=serialization.Encoding.PEM,
      format=serialization.PrivateFormat.TraditionalOpenSSL,
      encryption_algorithm=serialization.NoEncryption()
    )

def decode(pem):
  if "PUBLIC KEY" in pem:
    return serialization.load_pem_public_key(
      pem,
      backend=default_backend()
    )
  else:
    return serialization.load_pem_private_key(
      pem,
      password=None,
      backend=default_backend()
    )

def sign(payload, key):
  return key.sign(
    payload,
    padding.PSS(
      mgf=padding.MGF1(hashes.SHA256()),
      salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
  )
  
def validate(message, signature, key):
  key.verify(
    str(signature),
    str(message),
    padding.PSS(
      mgf=padding.MGF1(hashes.SHA256()),
      salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
  )

if __name__ == "__main__":
  key, public = generate_key_pair()
  key_pem = encode(key)
  public_pem = encode(public)

  print key_pem
  print public_pem

  key_loaded = decode(key_pem)
  public_loaded = decode(public_pem)

  data = {
    "name"   : "test name",
    "pass"   : "test pass",
    "pubkey" : public_pem,
  }
  payload = base64.b64encode(json.dumps(data, sort_keys=True))
  signature = sign(payload, key_loaded)
  validate(payload, signature, public_loaded)

  msg = {
    "data" : data,
    "payload": payload,
    "signature" : base64.b64encode(signature)
  }

  print json.dumps(msg, indent=2)
