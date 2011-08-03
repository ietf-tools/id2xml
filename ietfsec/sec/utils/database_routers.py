class DBRouter(object):
    """A router to control all database operations for the interim app"""

    # list of models that reside in the secondary database
    interim_models = ('InterimMeeting', 'InterimFile', 'InterimSlide',
                      'InterimMinute', 'InterimAgenda')

    def db_for_read(self, model, **hints):
        if model.__name__ in self.interim_models:
            return 'ietf_ams'
        return None

    def db_for_write(self, model, **hints):
        if model.__name__ in self.interim_models:
            return 'ietf_ams'
        return None
