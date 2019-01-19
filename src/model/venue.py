from timeslot import TimeSlot

class Venue:

    def __init__(self, id, name):
        # do some requests to get venue data
        # dummy
        self.name = "name"
        self.id = id

    @classmethod
    def fromDB(cls, id):
        name = ""
        return cls(id, name)

    @staticmethod
    def getVenues():
        venues = []
        return venues