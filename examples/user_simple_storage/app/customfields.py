import marshmallow.fields
from validate_email import validate_email
import phonenumbers


class Email(marshmallow.fields.Field):

    def __init__(self, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)

    def _deserialize(self, value, attr, obj):
        value = value.strip().lower()
        if not validate_email(value):
            self.fail('validator_failed')
        return value


class PhoneNumber(marshmallow.fields.Field):

    def __init__(self, *args, **kwargs):
        super(PhoneNumber, self).__init__(*args, **kwargs)

    @classmethod
    def phone_validator(cls, phone):
        try:
            if not phone.startswith('+'):
                phone = '+3' + phone
            obj = phonenumbers.parse(phone, None)
            return phonenumbers.is_valid_number(obj)
        except:
            pass
        return False

    @classmethod
    def convert_phone(cls, phone):
        if not phone.startswith('+'):
                phone = '+1' + phone
        obj = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(obj, phonenumbers.PhoneNumberFormat.E164)

    def _deserialize(self, value, attr, obj):
        if not self.phone_validator(value):
            self.fail('validator_failed')
        phone = self.convert_phone(value)
        return phone

