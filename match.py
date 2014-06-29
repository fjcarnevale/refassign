from google.appengine.ext import ndb

class Referee(ndb.Model):
	name = ndb.StringProperty()
	email = ndb.StringProperty()

class Field(ndb.Model):
	name = ndb.StringProperty()
	location = ndb.StringProperty()

class Match(ndb.Model):
	date = ndb.DateTimeProperty()
	field = ndb.KeyProperty()
	home = ndb.StringProperty()
	away = ndb.StringProperty()
	referees = ndb.KeyProperty(repeated=True)



