class CustomExceptions(Exception):
    """Base Exception class for Daily Checks"""
    pass

class ArgumentError(CustomExceptions):
    def __init__(self,*args, **kwargs):
        super(CustomExceptions, self ).__init__(*args)