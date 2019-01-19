class User:
    currentUser = None

    def __init__(self, name, token):
        self.name = name
        self.token = token

    @staticmethod
    def register(name, userid):
        # do a server request
        User.currentUser = User(name, userid)

    @staticmethod
    def login(userid):
        # do a server request
        # dummy for testing
        User.currentUser = User("test", userid)
