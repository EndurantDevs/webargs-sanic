from marshmallow import ValidationError, fields
from validate_email import validate_email
import phonenumbers


class Email(fields.Field):
    default_error_messages = {
        "invalid": "Not a valid email address.",
    }

    def __init__(self, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)

    def _deserialize(self, value, attr, data, **kwargs):
        value = value.strip().lower()
        if not validate_email(value):
            raise ValidationError(self.error_messages["invalid"])
        return value


class PhoneNumber(fields.Field):
    default_error_messages = {
        "invalid": "Not a valid phone number.",
    }

    def __init__(self, *args, **kwargs):
        super(PhoneNumber, self).__init__(*args, **kwargs)

    @classmethod
    def phone_validator(cls, phone):
        try:
            if not phone.startswith('+'):
                phone = '+3' + phone
            obj = phonenumbers.parse(phone, None)
            return phonenumbers.is_valid_number(obj)
        except Exception:
            return False
        return False

    @classmethod
    def convert_phone(cls, phone):
        if not phone.startswith('+'):
                phone = '+1' + phone
        obj = phonenumbers.parse(phone, None)
        return phonenumbers.format_number(obj, phonenumbers.PhoneNumberFormat.E164)

    def _deserialize(self, value, attr, data, **kwargs):
        if not self.phone_validator(value):
            raise ValidationError(self.error_messages["invalid"])
        phone = self.convert_phone(value)
        return phone
