# lib/custom.py 
# Custom validation functions and methods

from marshmallow import Schema, fields, validates, ValidationError, post_load
from pprint import pprint

# toy validation function
def validate_toy(toy):
    toys = ["ball", "stuffed", "squeak", "plush", "feather"]
    if not any(t in toy for t in toys):
        raise ValidationError(f"Must include one of: {', '.join(toys)}.")

# model 

class Cat:
    def __init__(self, name, coat, dob, favorite_toys = []):
        self.name = name
        self.coat = coat
        self.dob = dob
        self.favorite_toys = favorite_toys

# schema

class CatSchema(Schema):
    
    @validates("coat")
    def validate_coat( self, value ):
        coat_colorings = ["Tortoiseshell", "Calico", "Tabby", "Black", "Gray", "White", "Tuxedo"]
        if value not in coat_colorings:
            raise ValidationError(f"Must be one of: {', '.join(coat_colorings)}.")

    name = fields.Str(required=True, error_messages={"required": "Name is required."})
    dob = fields.Date(format="%Y-%m-%d")
    coat = fields.Str()
    favorite_toys = fields.List(fields.Str(validate=validate_toy))
      
    @post_load
    def make_cat(self, data, **kwargs):
        return Cat(**data)

# validate during deserialization

cat_data = [
    {"name": "Meowie","dob": "2020-11-28", "coat": "Calico",  "favorite_toys": ["ball"]}, # valid
    {"coat": "Tabby"},                                    # name is required
    {"name": "Fluffy", "dob": "June 1, 1980"},            # invalid dob
    {"name": "Whiskers", "coat": "Pink"},                 # invalid coat
    {"name": "Purry", "favorite_toys": ["my plants"] }    # invalid favorite_toy
]

try:
    CatSchema(many=True).load(cat_data)
except ValidationError as err:
    pprint(err.messages)
    # => {1: {'name': ['Name is required.']},
    # =>  2: {'dob': ['Not a valid date.']},
    # =>  3: {'coat': ['Must be one of: Tortoiseshell, Calico, Tabby, Black, Gray, White, Tuxedo .]},
    # =>  4: {'favorite_toys': {0: ['Must include one of: ball, stuffed, squeak, plush, feather.']}}}