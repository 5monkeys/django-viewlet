from django.template import TemplateSyntaxError

DEPRECATED_KEY_FORMAT_MESSAGE = (
    "Key argument format has been changed. It can be a function or "
    "a string containing `{args}`"
)

WRONG_KEY_FORMAT_MESSAGE = (
    "If you want to use your custom key for a viewlet which has arguments, "
    "please add `{args}` to the key where the arguments will be inserted."
)


class ViewletException(Exception):
    pass


class UnknownViewlet(TemplateSyntaxError):
    pass


class DeprecatedKeyFormat(ViewletException):
    def __init__(self, message=None):
        ViewletException.__init__(self, message or DEPRECATED_KEY_FORMAT_MESSAGE)


class WrongKeyFormat(ViewletException):
    def __init__(self, message=None):
        ViewletException.__init__(self, message or WRONG_KEY_FORMAT_MESSAGE)
