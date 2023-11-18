# lib/schema.py 

from marshmallow import Schema, fields, validates_schema, ValidationError 
from pprint import pprint

class VetSchema(Schema):
    
    name = fields.Str()
    accepting_new_clients = fields.Boolean()
    retired = fields.Boolean()
    
    @validates_schema
    def validate_schema(self, data, **kwargs):
        # "accepting_new_clients" and "retired" are not required fields, check for presence prior to getting values from dictionary
        if all(k in data.keys() for k in ["accepting_new_clients", "retired"]):
            if data["accepting_new_clients"] and data["retired"]:
                raise ValidationError(f"retired and accepting_new_clients are both true")    

# schema-level validation

vet_data = [
    {"name": "Dr. A",  "retired": False, "accepting_new_clients": False},
    {"name": "Dr. B",  "retired": False, "accepting_new_clients": True},
    {"name": "Dr. C",  "retired": True, "accepting_new_clients": False},
    {"name": "Dr. D",  "retired": True, "accepting_new_clients": True}  #invalid field combination 
]

try:
    VetSchema(many=True).load(vet_data)
except ValidationError as err:
    pprint(err.messages)
    # => {3: {'_schema': ['retired and accepting_new_clients are both true']}}
    