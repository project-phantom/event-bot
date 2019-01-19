from booking import Booking

class Event:
    def __init__(self, organizerID, name, description, visibility, booking, attendee):
        # fetch data from server
        self.organizerID = organizerID
        self.name = name
        self.description = description
        self.visibility = visibility
        self.booking = booking
        self.attendee = attendee

    @classmethod
    def createEvent(cls, organizerID, name, description):
        return cls(organizerID, name, description, 0, None, [])
    
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
    
