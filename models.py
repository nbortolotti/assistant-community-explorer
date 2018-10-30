from google.appengine.ext import ndb

class Settings(ndb.Model):
    name = ndb.StringProperty()
    value = ndb.StringProperty()

    @staticmethod
    def get(name):
        NOT_SET_VALUE = "not set"
        retval = Settings.query(Settings.name == name).get()
        if not retval:
            retval = Settings()
            retval.name = name
            retval.value = NOT_SET_VALUE
            retval.put()
        return retval.value
