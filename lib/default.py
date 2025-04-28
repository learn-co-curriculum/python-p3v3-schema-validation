# lib/default.py 

from marshmallow import Schema, fields
from datetime import datetime
import uuid
from pprint import pprint

class OwnerSchema(Schema):
    id = fields.UUID(load_default=uuid.uuid1)                       # default if missing during deserialization
    birthdate = fields.DateTime(dump_default=datetime(2017, 9, 29)) # default if missing during serialization

pprint( OwnerSchema().load({}))
# {'id': UUID('337d946c-32cd-11e8-b475-0022192ed31b')}

pprint(OwnerSchema().dump({}))
# {'birthdate': '2017-09-29T00:00:00'}



