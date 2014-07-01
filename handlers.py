import datetime
import os
import urllib2

from google.appengine.api import mail
from google.appengine.ext import ndb

import jinja2
import webapp2
from webapp2_extras import sessions

import match

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

# Sourced from https://webapp-improved.appspot.com/api/webapp2_extras/sessions.html
class BaseHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class Index(BaseHandler):
	""" Handles requests to the main page """
	def get(self):
		matches = match.Match.query()

		
class AddTeam(BaseHandler):
	def get(self):
		team = match.Team()
		team.name = self.request.get("name")
		team.league = ndb.Key(urlsafe = self.request.get("league"))
		team.put()
		
		self.response.write("Created team %s in league %s" % (team.name, team.league.get().name))

class AddRef(BaseHandler):
	def get(self):
		ref = match.Referee()
		ref.name = self.request.get("name")
		ref.email = self.request.get("email")
		ref.grade = int(self.request.get("grade"))
		
		leagues = [ndb.Key(urlsafe=league) for league in self.request.get("league", allow_multiple=True)]

		ref.leagues = leagues
		ref.put()
		
		self.response.write("Created ref %s" % ref.name)

class AddField(BaseHandler):
	def get(self):
		field = match.Field()
		field.name = self.request.get("name")
		field.location = self.request.get("location")
		field.put()
		
		self.response.write("Created field %s at %s" % (field.name, field.location))

class AddLeague(BaseHandler):
	def get(self):
		league = match.League()
		league.name = self.request.get("name")
		league.put()		

		self.response.write("Created league %s" % league.name)

class AddMatch(BaseHandler):
	def get(self):
		m = match.Match()
		m.date = datetime.datetime.strptime(self.request.get("date"), "%Y-%m-%dT%H:%M")
		
		team_keys = self.request.get('team', allow_multiple=True)

		for tk in team_keys:
			m.teams.append(ndb.Key(urlsafe=tk))

		ref_key = self.request.get('ref')
		m.referees.append(ndb.Key(urlsafe=ref_key))		

		field_key = self.request.get('field')
		m.field = ndb.Key(urlsafe=field_key)

		refs = [ref.get() for ref in m.referees]
		teams = [team.get() for team in m.teams]

		template_values = {"match":m, "referees":refs, "teams":teams, "field":m.field.get()}
		template = JINJA_ENVIRONMENT.get_template('match.json')
		self.response.write(template.render(template_values))

class CreateRef(BaseHandler):
	def get(self):
		leagues = match.League.query()

		template_values = {"leagues":leagues}
		template = JINJA_ENVIRONMENT.get_template('dynamic/create_ref.html')
		self.response.write(template.render(template_values))

class CreateTeam(BaseHandler):
	def get(self):
		leagues = match.League.query()

		template_values = {"leagues":leagues}
		template = JINJA_ENVIRONMENT.get_template('dynamic/create_team.html')
		self.response.write(template.render(template_values))

class CreateMatch(BaseHandler):
	def get(self):
		teams = match.Team.query()
		refs = match.Referee.query()
		fields = match.Field.query()

		template_values = {"teams":teams, "refs":refs, "fields":fields}
		template = JINJA_ENVIRONMENT.get_template('dynamic/create_match.html')
		self.response.write(template.render(template_values))

class GetReferees(BaseHandler):
	def get(self):
		league_key = self.request.get("league")
		league = ndb.Key(urlsafe=league_key).get()
		
		refs = [ref.get() for ref in league.referees]

		template_values = {"referees":refs}
		template = JINJA_ENVIRONMENT.get_template('referee.json')
		self.response.write(template.render(template_values))



