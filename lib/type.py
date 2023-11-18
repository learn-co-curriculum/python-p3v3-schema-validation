# lib/type.py 

from marshmallow import Schema, fields, ValidationError
from pprint import pprint

class UserSchema(Schema):
    name = fields.Str()                 
    age = fields.Int()     
    email = fields.Email() 

user_data = [
    {"name": "Ariel", "age": 30,  "email": "ariel@example.com"},      # valid data types 
    {"name": True, "age": 42,  "email": "someone@example..com"},      # invalid name
    {"name": "Sasha", "age": "young",  "email": "ariel@example.com"}, # invalid age
    {"name": "Cruz", "age": 88,  "email": "cruz@example..com"},       # invalid email
]

# validate and deserialize the data

UserSchema(many=True).load(user_data)  #raises ValidationError
