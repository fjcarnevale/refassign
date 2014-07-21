from google.appengine.ext import ndb

class Person(ndb.Model):
	name = ndb.StringProperty()
	email = ndb.StringProperty()

class Referee(Person):
	grade = ndb.IntegerProperty()
	leauges = ndb.KeyProperty()

class Assigner(Person):
	leagues = ndb.KeyProperty(repeated=True)

class Field(ndb.Model):
	name = ndb.StringProperty()
	location = ndb.StringProperty()


class League(ndb.Model):
	name = ndb.StringProperty()
	assigners = ndb.KeyProperty(repeated=True)
	referees = ndb.KeyProperty(repeated=True)
	teams = ndb.KeyProperty(repeated=True)
	# maybe the league should also hold matches,
	# otherwise may have to watch out for duplicates when retreiving from teams

	@staticmethod
	def new_league(name, assigners=[], referees=[], teams=[]):
		league = League()
		league.populate(name=name, assigners=assigners, referees=referees, teams=teams)
		return league

	def add_new_team(self, name):
		team = Team.new_team(name,self)
		team_key = team.put()

		self.teams.append(team_key)
		self.put()
		return team_key

class Team(ndb.Model):
	name = ndb.StringProperty()
	league = ndb.KeyProperty()
	matches = ndb.KeyProperty(repeated=True)

	@staticmethod
	def new_team(name, league):
		team = Team()
		team.populate(name = name, league = league.key)
		return team

class Match(ndb.Model):
	date = ndb.DateTimeProperty()
	field = ndb.KeyProperty()
	teams = ndb.KeyProperty(repeated=True)
	referees = ndb.KeyProperty(repeated=True)



