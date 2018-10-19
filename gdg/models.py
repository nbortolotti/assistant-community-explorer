from google.appengine.ext import ndb

# change for component dependency
class gdgchapter(ndb.Model):
    create_date = ndb.DateTimeProperty(auto_now_add=True)
    groupName = ndb.StringProperty()
    groupStatus = ndb.StringProperty()
    groupMembers = ndb.IntegerProperty()
    city = ndb.StringProperty()
    countryMod =  ndb.StringProperty()