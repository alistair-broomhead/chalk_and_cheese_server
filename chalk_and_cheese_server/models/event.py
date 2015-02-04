class Event(object):
    
    audit = []

    def __init__(self, event_type, data):
        self.event_type = event_type
        self.data = data
        self.audit.append(self)

    def __str__(self):
        return 'Event({0}, {1})'.format(
            self.event_type, self.data
        )