# lib/partial.py

from marshmallow import Schema, fields
from pprint import pprint

class UserSchema(Schema):
    name = fields.String(required=True)
    age = fields.Integer(required=True)

result_1 = UserSchema().load({"name": "Noam", "age": 42})  #name and age required
pprint(result_1)  # => {'age': 42, 'name': 'Noam'}

result_2 = UserSchema().load({"age": 42}, partial=("name",))  #age required
# OR UserSchema(partial=('name',)).load({'age': 42})
pprint(result_2)  # => {'age': 42}