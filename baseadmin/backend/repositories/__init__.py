from baseadmin.storage import db
from baseadmin.pki     import keys

# FIXME: required to make sure the keys are initialized
keys.private

from mqfactory                      import Threaded, MessageQueue
from mqfactory.transport.mqtt       import MQTTTransport
from mqfactory.transport.qos        import Acknowledging
from mqfactory.message.format.js    import JsonFormatting
from mqfactory.store                import Persisting
from mqfactory.store.mongo          import MongoCollection
from mqfactory.message.security     import Signing
from mqfactory.message.security.rsa import RsaSignature
from mqfactory.message.security.rsa import generate_key_pair, encode

mq = JsonFormatting(
       Signing(
         Acknowledging(
           Persisting(
             Threaded(
               MessageQueue(
                 MQTTTransport("mqtt://localhost:1883")
               )
             ),
             inbox=MongoCollection(db.inbox),
             outbox=MongoCollection(db.outbox)
           )
         ),
         adding=RsaSignature(MongoCollection(db.pki), me="")
       )
     )

mq.send("everybody", "hello...")
