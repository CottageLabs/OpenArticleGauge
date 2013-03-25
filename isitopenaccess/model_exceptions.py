class LookupException(Exception):
    def __init__(self, message):
        self.message = message
        super(LookupException, self).__init__(self, message)
