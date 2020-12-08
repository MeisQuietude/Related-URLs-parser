import validator_collection as validation_lib


class Validator(object):

    @staticmethod
    def is_valid_email(email: str) -> bool:
        return validation_lib.email(email) is not None
