class NoteAppError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class InvalidKeyError(NoteAppError):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return self.message


class NoteNotFoundError(NoteAppError):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return self.message
