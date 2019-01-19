import datetime

class TimeSlot:
    def __init__(self, date, slot):
        if (not isinstance(date,datetime.date)):
            raise Exception("incorrect format")

        if (not isinstance(slot,int)):
            raise Exception("incorrect format")

        if (slot < 0 or slot > 24):
            raise Exception("incorrect format")

        self.date = date
        self.slot = slot
    
