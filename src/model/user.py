class User:
    def __init__(self, name, token):
        self.name = name
        self.token = token
    
    @staticmethod
    def register(name, userid):
        # do a server request
        return User(name, "T1231")