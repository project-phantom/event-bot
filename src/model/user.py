from dbhelper import DB

class User:
    currentUser = None

    def __init__(self, name, token):
        self.name = name
        self.token = token

    @staticmethod
    def register(name):
        token = DB().add_user(name)
        User.currentUser = User(name, token)
        return token

    @staticmethod
    def login(token):
        if (DB().user_login(token) is None):
            return False

        User.currentUser = User("test", token)
        return True

