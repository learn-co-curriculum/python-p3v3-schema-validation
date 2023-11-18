# Validation : Code-Along

## Learning Goals

- Handle validation errors that arise during deserialization.
- Recognize common field type errors.
- Define required fields.
- Use partial loading to skip required fields.
- Define default values for missing data.
- Use builtin field validators.
- Write custom field and schema validators.

---

## Key Vocab

- **Serialization**: a process to convert programmatic data such as a Python
  object to a sequence of bytes that can be shared with other programs,
  computers, or networks.
- **Deserialization**: the reverse process, converting input data back to
  programmatic data.
- **Validation**: a process for checking the validity of data such as the type,
  format, or values.
- **Schema**: A class used to validate, serialize, and deserialize data.

---

## Introduction

Data is validated during deserialization. A `ValidationError` exception is
raised when validation fails on a field or schema. The `marshmallow` library
provides many helpful built-in validators, and also lets us create custom
validators.

---

## Setup

This lesson is a code-along, so fork and clone the repo.

Run `pipenv install` to install the dependencies and `pipenv shell` to enter
your virtual environment before running your code.

```console
$ pipenv install
$ pipenv shell
```

---

## Type errors

A `marshmallow` schema defines variables that map attribute names to `Field`
objects, each specifying the expected data type using classes `field.Int()`,
`field.Str()`, etc.

Consider the code in `lib/type.py`, shown below. The schema loads a list
containing four dictionaries of user data. The first dictionary contains valid
user data in that the values provided match the field types defined by the
schema. However, the last three dictionaries each contain a type error with one
of the values.

```py
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

UserSchema(many=True).load(user_data)  #raises ValidationError
```

The schema `load()` and the JSON-decoding `loads()` methods both raise a
`ValidationError` error when invalid data are passed. Try running the code and
confirm the error shown below is raised. Since a collection is passed to the
`load()` method, the error message includes the indices of the invalid items.

```console
$ python lib/type.py
marshmallow.exceptions.ValidationError: {1: {'name': ['Not a valid string.'], 'email': ['Not a valid email address.']}, 2: {'age': ['Not a valid integer.']}, 3: {'email': ['Not a valid email address.']}}
```

The `ValidationError.messages` attribute can be used to access the dictionary of
validation errors, while the correctly deserialized data are accessible in
`ValidationError.valid_data`. Update the code as shown below to catch the errors
and print the valid and invalid data:

```py
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

try:
    UserSchema(many=True).load(user_data)

except ValidationError as err:
    print("Valid data:")
    pprint(err.valid_data)
    # => [{'age': 30, 'email': 'ariel@example.com', 'name': 'Ariel'},
    # =>  {'age': 42},
    # =>  {'email': 'ariel@example.com', 'name': 'Sasha'},
    # =>  {'age': 88, 'name': 'Cruz'}]

    print("Invalid data:")
    pprint(err.messages)
    # => {1: {'email': ['Not a valid email address.'], 'name': ['Not a valid string.']},
    # =>  2: {'age': ['Not a valid integer.']},
    # =>  3: {'email': ['Not a valid email address.']}}
```

Run the updated code and confirm the output:

```console
$ python lib/type.py

Valid data:
[{'age': 30, 'email': 'ariel@example.com', 'name': 'Ariel'},
 {'age': 42},
 {'email': 'ariel@example.com', 'name': 'Sasha'},
 {'age': 88, 'name': 'Cruz'}]
Invalid data:
{1: {'email': ['Not a valid email address.'], 'name': ['Not a valid string.']},
 2: {'age': ['Not a valid integer.']},
 3: {'email': ['Not a valid email address.']}}
```

---

## Required fields

Fields defined in a schema are optional by default, and thus need not be
included in the data passed to the deserialization methods. A field can be
denoted as required by passing `required=True` as a parameter. For example, the
schema below defines `name` as a required field, while `breed` is optional.

```py
class HamsterSchema(Schema):
     name = fields.Str(required=True)
     breed = fields.Str()
```

Consider the code in `lib/required.py`. The schema loads a list containing four
dictionaries of hamster data. The first two contain valid hamster data in that
the required field `name` is provided, while the last two are missing the
required field.

```py
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

result = HamsterSchema(many=True).load(hamster_data)
pprint(result)   # line not reached due to ValidationError
```

Run the code and confirm the validation error is raised:

```console
$ python lib/required.py
marshmallow.exceptions.ValidationError: {2: {'name': ['Missing data for required field.']}, 3: {'name': ['Missing data for required field.']}}
```

Let's update the code to catch the errors and print the valid and invalid data:

```py
try:
    HamsterSchema(many=True).load(hamster_data)

except ValidationError as err:
    print("Valid data:")
    pprint(err.valid_data)
    # => [{'breed': 'Syrian', 'name': 'Hammy'},
    # => {'name': 'Wiggles'},
    # => {'breed': 'Winter White'},
    # => {}]
    print("Invalid data:")
    pprint(err.messages)
    # => {2: {'name': ['Missing data for required field.']},
    # => 3: {'name': ['Missing data for required field.']}}
```

Run the code to confirm the output:

```console
$ python lib/required.py
Valid data:
[{'breed': 'Syrian', 'name': 'Hammy'},
 {'name': 'Wiggles'},
 {'breed': 'Winter White'},
 {}]
Invalid data:
{2: {'name': ['Missing data for required field.']},
 3: {'name': ['Missing data for required field.']}}
```

---

## Skipping Required Fields (i.e. Partial-Loading)

If the same schema is used to deserialize data in multiple scenarios, you can
selectively skip required validation by passing a partial parameter to the
loading method or to the schema constructor as shown below:

```py
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
```

---

## Default Values

When defining a schema field, the parameter `load_default` specifies the default
deserialization value for a field, while `dump_default` specifies the default
serialization value.

```py
# lib/default.py

from marshmallow import Schema, fields
from datetime import datetime
import uuid
from pprint import pprint

class OwnerSchema(Schema):
    id = fields.UUID(load_default=uuid.uuid1)       # deserialization default value
    dob = fields.DateTime(dump_default=datetime(2017, 9, 29)) # serialization default value

pprint( OwnerSchema().load({}))     # id is missing, will be assigned default value
# {'id': UUID('337d946c-32cd-11e8-b475-0022192ed31b')}

pprint(OwnerSchema().dump({}))     # dob is missing, will be assigned default value
# {'dob': '2017-09-29T00:00:00'}
```

---

## Unknown Fields

By default, a `ValidationError` is raised during loading if the data includes a
key with no matching field in the schema. The code in `lib/unknown.py` raises a
`ValidationError` due to the unknown field `is_friendly` passed in as data.

```py
# lib/unknown.py

from marshmallow import Schema, fields, post_load, ValidationError

# model

class Dog:
    def __init__(self, name, breed, tail_wagging = False):
        self.name = name
        self.breed = breed
        self.tail_wagging = tail_wagging

# schema

class DogSchema(Schema):
    name = fields.Str()
    breed = fields.Str()
    tail_wagging = fields.Boolean()

# validate during deserialization

friendly_dog = '{"name": "Snuggles","breed": "Beagle", "tail_wagging": true, "is_friendly" : true}'

try:
    result = DogSchema().loads(friendly_dog)
    pprint(result)  # line not reached if ValidationError is raised

except ValidationError as err:
    print(err.messages)    # {'is_friendly': ['Unknown field.']}
    print(err.valid_data)  # {'name': 'Snuggles', 'breed': 'Beagle', 'tail_wagging': True}
```

This behavior can be modified with the `unknown` option, which accepts one of
the following values:

- RAISE (default): raise a ValidationError if there are any unknown fields
- EXCLUDE: exclude unknown fields from the deserialized result
- INCLUDE: include the unknown fields in the deserialized result

You can specify the option during schema instantiation
`DogSchema(unknown=INCLUDE)` or during loading
`DogSchema().load(friendly, unknown=INCLUDE)`.

Experiment with alternatively passing `EXCLUDE` and `INCLUDE` to see the
deserialized result.

---

## Builtin Field Validators

We've seen how marshmallow supports builtin validation for field data types.

```py
# lib/builtin.py

from marshmallow import Schema, fields, validate, ValidationError
from pprint import pprint

class VetSchema(Schema):

    name = fields.Str()
    email = fields.Email()   #Email has built-in validation
    website = fields.URL()   #URL has built-in validation
    specialty = fields.Str()
    years_practice = fields.Int()
    diploma = fields.Str()


vet_data = [
    {"name": "Dr. Wags", "email": "email.com"},                                     # invalid email
    {"name": "Dr. Wags", "email": "wags@email.com",  "website": "htp:company.com"}, # invalid URL
    {"name": "Dr. Wags", "email": "wags@email.com",  "specialty": ""} ,
    {"name": "Dr. Wags", "email": "wags@email.com",  "years_practice": -5},
    {"name": "Dr. Wags", "email": "wags@email.com", "diploma": "none"},
    {"name": "Mr. Wags", "email": "wags@email.com"},
]

try:
    result = VetSchema(many=True).load(vet_data)
    pprint(result)
except ValidationError as err:
    pprint(err.messages)
    # => 0: {'email': ['Not a valid email address.']},
    # => 1: {'website': ['Not a valid URL.']},
```

For example, running the code in `lib/builtin.py` results in validation errors
for the first two dictionaries due to an invalid email and invalid URL.

```console
$ python lib/builtin.py
{0: {'email': ['Not a valid email address.']},
 1: {'website': ['Not a valid URL.']}}
```

Beyond data type validation and required fields, you can perform additional
validation for a field by passing the `validate` argument. There are a number of
built-in validators in the marshmallow.validate module.

Suppose we need to add the following field validation:

- `specialty` should not be an empty string
- `years_practice` should be an integer between 0 and 100, inclusive.
- `diploma` should be either "DVM" or "VMD".

We can achieve this by using one of the builtin
[marshmallow validators](https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html#api-validators)
(there are lots of them!) as shown:

```py
specialty = fields.Str(validate=validate.Length(min=1))
years_practice = fields.Int(validate=validate.Range(min=0, max=100),  )
diploma = fields.Str(validate=validate.OneOf(["DVM", "VMD"]))
```

Let's add one more rule to our schema:

- `name` should start with "Dr."

We could use a builtin regular expression for this, but let's see how to pass a
callable to `validate`. This let's us write any boolean expression as a
validator, including calling Python's `startswith()` string method:

```py
name = fields.Str(validate=lambda str: str.startswith("Dr."))
```

Update `lib/builtin.py` to add a validator to each of the `name`, `specialty`,
`years_practice`, and `diploma` fields. Now, all of the data passed in for
loading should fail validation.

```py
# lib/builtin.py

from marshmallow import Schema, fields, validate, ValidationError
from pprint import pprint

class VetSchema(Schema):

    name = fields.Str(validate=lambda str: str.startswith("Dr."))
    email = fields.Email()   #Email has built-in validation
    website = fields.URL()   #URL has built-in validation
    specialty = fields.Str(validate=validate.Length(min=1))
    years_practice = fields.Int(validate=validate.Range(min=0, max=100),  )
    diploma = fields.Str(validate=validate.OneOf(["DVM", "VMD"]))

# field-level validation

vet_data = [
    {"name": "Dr. Wags", "email": "email.com"},                                     # invalid email
    {"name": "Dr. Wags", "email": "wags@email.com",  "website": "htp:company.com"}, # invalid URL
    {"name": "Dr. Wags", "email": "wags@email.com",  "specialty": ""} ,             # invalid specialty
    {"name": "Dr. Wags", "email": "wags@email.com",  "years_practice": -5},         # invalid years of practice
    {"name": "Dr. Wags", "email": "wags@email.com", "diploma": "none"},             # invalid diploma
    {"name": "Mr. Wags", "email": "wags@email.com"},                                # invalid name
]

try:
    result = VetSchema(many=True).load(vet_data)
    pprint(result)
except ValidationError as err:
    pprint(err.messages)
    # => 0: {'email': ['Not a valid email address.']},
    # => 1: {'website': ['Not a valid URL.']},
    # => 2: {'specialty': ['Shorter than minimum length 1.']},
    # => 3: {'years_practice': ['Must be greater than or equal to 0 and less than or equal to 100.']}},
    # => 4: {'diploma': ['Must be one of: DVM, VMD.']}},
    # => 5: {'name': ['Invalid value.']}}
```

Confirm each field validator triggers an error message:

```console
$ python builtin.py

{0: {'email': ['Not a valid email address.']},
 1: {'website': ['Not a valid URL.']},
 2: {'specialty': ['Shorter than minimum length 1.']},
 3: {'years_practice': ['Must be greater than or equal to 0 and less than or '
                        'equal to 100.']},
 4: {'diploma': ['Must be one of: DVM, VMD.']},
 5: {'name': ['Invalid value.']}}
```

---

## Schema Validation

So far we've seen how to perform validation on an individual field. Sometimes we
need to perform schema-level validation, where we may need to check data values
across multiple fields.

Consider the schema in `lib/schema.py` that describes the data for a veterinary
doctor. We may want to add a validation rule that the two boolean fields
`accepting_new_clients` and`retired` should not both be true. Schema-level
validation can be implemented using a method decorated with `@validates_schema`
as shown below. The method raises a `ValidationError` if both fields are true.
The outer conditional is needed to avoid a error in accessing a dictionary key
since the schema fields are not required.

```py
# lib/schema.py

from marshmallow import Schema, fields, validates_schema, ValidationError
from pprint import pprint

class VetSchema(Schema):

    name = fields.Str()
    accepting_new_clients = fields.Boolean()
    retired = fields.Boolean()

    @validates_schema
    def validate_schema(self, data, **kwargs):
        # "accepting_new_clients" and "retired" are not required fields, check for their presence prior to getting values from dictionary
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
```

---

## Custom Field Validators

Finally, `lib/custom.py` shows an example of custom validation functions and
custom error messages.

- The `name` field defines a custom error message when the required field is
  absent.
- The `dob` field defines a specific date format.
- The `coat` field is validate using a custom validation method decorated by
  `@validates("coat")`.
- The `favorite_toys` field list items are validated using the function
  `validate_toy`.

```py
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
```

Run the program to confirm the validation error message:

```console
{1: {'name': ['Name is required.']},
 2: {'dob': ['Not a valid date.']},
 3: {'coat': ['Must be one of: Tortoiseshell, Calico, Tabby, Black, Gray, '
              'White, Tuxedo.']},
 4: {'favorite_toys': {0: ['Must include one of: ball, stuffed, squeak, plush, '
                           'feather.']}}}
```

---

## Conclusion

The `marshmallow` library includes many builtin validators. We've looked at just
a few, but you can see how helpful they are in restricting data values during
deserialization. We can also write custom validators, along with customizing the
error messages included during deserialization.

## Solution Code

```py
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

try:
    UserSchema(many=True).load(user_data)

except ValidationError as err:
    print("Valid data:")
    pprint(err.valid_data)
    # => [{'age': 30, 'email': 'ariel@example.com', 'name': 'Ariel'},
    # =>  {'age': 42},
    # =>  {'email': 'ariel@example.com', 'name': 'Sasha'},
    # =>  {'age': 88, 'name': 'Cruz'}]

    print("Invalid data:")
    pprint(err.messages)
    # => {1: {'email': ['Not a valid email address.'], 'name': ['Not a valid string.']},
    # =>  2: {'age': ['Not a valid integer.']},
    # =>  3: {'email': ['Not a valid email address.']}}
```

```py
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

try:
    HamsterSchema(many=True).load(hamster_data)

except ValidationError as err:
    print("Valid data:")
    pprint(err.valid_data)
    # => [{'breed': 'Syrian', 'name': 'Hammy'},
    # => {'name': 'Wiggles'},
    # => {'breed': 'Winter White'},
    # => {}]
    print("Invalid data:")
    pprint(err.messages)
    # => {2: {'name': ['Missing data for required field.']},
    # => 3: {'name': ['Missing data for required field.']}}
```

```py
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
```

```py
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
```

```py
# lib/validate_unknown.py

from marshmallow import Schema, fields, post_load, ValidationError

# model

class Dog:
    def __init__(self, name, breed, tail_wagging = False):
        self.name = name
        self.breed = breed
        self.tail_wagging = tail_wagging

# schema

class DogSchema(Schema):
    name = fields.Str()
    breed = fields.Str()
    tail_wagging = fields.Boolean()

    @post_load
    def make_dog(self, data, **kwargs):
        return Dog(**data)

# validate during deserialization

friendly_dog = '{"name": "Snuggles","breed": "Beagle", "tail_wagging": true, "is_friendly" : true}'

try:
    result = DogSchema().loads(friendly_dog)
    pprint(result)  # line not reached if error thrown

except ValidationError as err:
    print(err.messages)    # {'is_friendly': ['Unknown field.']}
    print(err.valid_data)  # {'name': 'Snuggles', 'breed': 'Beagle', 'tail_wagging': True}
```

```py
# lib/builtin.py

from marshmallow import Schema, fields, validate, ValidationError
from pprint import pprint

class VetSchema(Schema):

    name = fields.Str(validate=lambda str: str.startswith("Dr."))
    email = fields.Email()   #Email has built-in validation
    website = fields.URL()   #URL has built-in validation
    specialty = fields.Str(validate=validate.Length(min=1))
    years_practice = fields.Int(validate=validate.Range(min=0, max=100),  )
    diploma = fields.Str(validate=validate.OneOf(["DVM", "VMD"]))

# field-level validation

vet_data = [
    {"name": "Dr. Wags", "email": "email.com"},                                     # invalid email
    {"name": "Dr. Wags", "email": "wags@email.com",  "website": "htp:company.com"}, # invalid URL
    {"name": "Dr. Wags", "email": "wags@email.com",  "specialty": ""} ,             # invalid specialty
    {"name": "Dr. Wags", "email": "wags@email.com",  "years_practice": -5},         # invalid years of practice
    {"name": "Dr. Wags", "email": "wags@email.com", "diploma": "none"},             # invalid diploma
    {"name": "Mr. Wags", "email": "wags@email.com"},                                # invalid name
]

try:
    result = VetSchema(many=True).load(vet_data)
    pprint(result)
except ValidationError as err:
    pprint(err.messages)
    # => 0: {'email': ['Not a valid email address.']},
    # => 1: {'website': ['Not a valid URL.']},
    # => 2: {'specialty': ['Shorter than minimum length 1.']},
    # => 3: {'years_practice': ['Must be greater than or equal to 0 and less than or equal to 100.']}},
    # => 4: {'diploma': ['Must be one of: DVM, VMD.']}},
    # => 5: {'name': ['Invalid value.']}}
```

```py
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
```

```py
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
```

---

## Resources

- [marshmallow](https://pypi.org/project/marshmallow/)
- [marshmallow quickstart](https://marshmallow.readthedocs.io/en/stable/quickstart.html)
- [marshmallow validator](https://marshmallow.readthedocs.io/en/stable/marshmallow.validate.html#api-validators)
