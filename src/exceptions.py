class CustomExceptionBase(Exception):
    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)


class UniqueError(CustomExceptionBase):
    pass


class DatabaseError(CustomExceptionBase):
    pass


