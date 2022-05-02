import sqlalchemy as sa

# class IntEnum(db.TypeDecorator):
#     """
#     Enables passing in a Python enum and storing the enum's *value* in the db.
#     The default would have stored the enum's *name* (ie the string).
#     """
#     impl = db.Integer
#
#     def __init__(self, enumtype, *args, **kwargs):
#         super(IntEnum, self).__init__(*args, **kwargs)
#         self._enumtype = enumtype
#
#     def process_bind_param(self, value, dialect):
#         if isinstance(value, int):
#             return value
#
#         return value.value
#
#     def process_result_value(self, value, dialect):
#         return self._enumtype(value)


class IntEnum(sa.types.TypeDecorator):
    impl = sa.Integer
    def __init__(self, enumtype, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)