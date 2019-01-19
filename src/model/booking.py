from src.model.timeslot import TimeSlot as slot
from src.model.venue import Venue
import requests

class Booking: 
    def __init__(self, venue, status):
        if not isinstance(venue, Venue):
            raise TypeError()

        self.slots = set()
        self.venue = venue
        self.status = status

    # check if the slot is bookable
    def isBookable(self):
        # do some server request
        return True

    def bookVenue(self):
        if not self.isBookable():
            return False

        # do some server request

    def addSlot(self, slot):
        if (isinstance(slot, int) and slot >= 0 and slot < 24):
            self.slots.add(slot)
            return True
        else:
            return False

    def removeSlot(self, slot):
        try:
            self.slots.remove(slot)
            return True
        except KeyError:
            return False

