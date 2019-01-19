from src.model.booking import Booking
from dbhelper import DB
from src.model.user import User

class Event:
    def __init__(self, id, organizerID, name, description, visibility, booking, attendee):
        # fetch data from server
        self.id = id
        self.organizerID = organizerID
        self.name = name
        self.description = description
        self.visibility = visibility
        self.booking = booking
        self.attendee = attendee

    @classmethod
    def createEvent(cls, organizerID, name, description):
        return DB().create_event(User.currentUser.token, name, "", "", description)
    
    @staticmethod
    def setName(id, name):
        return

    @staticmethod
    def getName(id):
        return ""

    @staticmethod
    def setDescription(id, description):
        return

    @staticmethod
    def getDescription(id):
        return

    @staticmethod
    def setVisibility(id, description):
        return

    @staticmethod
    def isVisible(id):
        return

    @staticmethod
    def getVisibleEvents():
        events = []
        return events
    
