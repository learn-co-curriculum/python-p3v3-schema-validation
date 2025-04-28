# lib/required.py

from marshmallow import Schema, fields, ValidationError
from pprint import pprint

# schema

class HamsterSchema(Schema):
     name = fields.Str(required=True)
     breed = fields.Str()

hamster_data = [
    {"name": "Hammy", "breed": "Syrian"},   # valid  
    {"name": "Wiggles"},                    # valid, breed is not required
    {"breed": "Winter White"},              # invalid, name is required
    {}                                      # invalid, name is required
]

HamsterSchema(many=True).load(hamster_data)  #raises ValidationError