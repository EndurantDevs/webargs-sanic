from webargs import fields
from webargs import validate
from app.customfields import PhoneNumber
from app.customfields import Email


user_data = {
    'phone_number': PhoneNumber(required=False),
    'email': Email(required=True),
    'password': fields.Str(required=False, validate=lambda value: len(value)>=8),
    'first_name': fields.Str(required=True, validate=lambda value: len(value)>=1),
    'last_name': fields.Str(required=True, validate=lambda value: len(value)>=1),
    'middle_name': fields.Str(),
    'gender': fields.Str(required=True, validate=validate.OneOf(["M", "F"])),
    'birth_date': fields.Date(required=False),
}

user_id = {
    'user_id': fields.Str(required=True, validate=lambda x:len(x)==32, location='query'),
}

user_update = {
    'user_data': fields.Nested({
        'phone_number': PhoneNumber(),
        'email': Email(),
        'password': fields.Str(validate=lambda value: len(value)>=8),
        'first_name': fields.Str(validate=lambda value: len(value)>=1),
        'last_name': fields.Str(validate=lambda value: len(value)>=1),
        'middle_name': fields.Str(),
        'gender': fields.Str(validate=validate.OneOf(["M", "F"])),
        'birth_date': fields.Date(),
    }),
    'user_id': user_id['user_id'],
}
