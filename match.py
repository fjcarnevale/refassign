from google.appengine.ext import ndb

class Referee(ndb.Model):
	name = ndb.StringProperty()
	email = ndb.StringProperty()

class Match(ndb.Model):
	date = ndb.DateTimeProperty()
	field = ndb.StringProperty()
	home = ndb.StringProperty()
	away = ndb.StringProperty()
	referees = ndb.KeyProperty(repeated=True)



