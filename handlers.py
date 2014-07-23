import datetime
import hashlib
import os
import random
import string
import urllib2

from google.appengine.api import mail
from google.appengine.ext import ndb

import jinja2
import webapp2
from webapp2_extras import sessions

import controllers
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

class Register(BaseHandler):
	def get(self):
		email = self.request.get("email")
		password = self.request.get("password")
		name = self.request.get("name")
		
		try:
			new_person = controllers.register_new_person(name,email,password)
			template_values = {"success":True}
			template = JINJA_ENVIRONMENT.get_template('dynamic/register_results.html')
			self.response.write(template.render(template_values))
		except Exception as e:
			template_values = {"success":False, "error":str(e)}
			template = JINJA_ENVIRONMENT.get_template('dynamic/register_results.html')
			self.response.write(template.render(template_values))
		

class Login(BaseHandler):
	def get(self):
		email = self.request.get("email")
		password = self.request.get("password")

		try:
			person = controllers.login_person(email,password)
			self.session['person_email'] = person.email
			print "Logged in as user %s" % person.name
		except Exception as e:
			print "Failed to login : %s" % str(e)

class LandingPage(BaseHandler):
	def get(self):
		person_email = self.session.get('person_email', None)

		if person_email is None:
			return redirect('/static/login.html')

		print "User %s is logged in" % person_email

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

class ViewLeagues(BaseHandler):
	def get(self):
		leagues = match.League.query()

		template_values = {"leagues":leagues}
		template = JINJA_ENVIRONMENT.get_template('dynamic/view_leagues.html')
		self.response.write(template.render(template_values))

class ViewMatches(BaseHandler):
	def get(self):
		leagues = match.League.query()

		template_values = {"leagues":leagues}
		template = JINJA_ENVIRONMENT.get_template('dynamic/view_matches.html')
		self.response.write(template.render(template_values))
		
class AddTeam(BaseHandler):
	def get(self):
		league_key = ndb.Key(urlsafe = self.request.get("league"))
		league = league_key.get()

		team_key = league.add_new_team(self.request.get("name"))
		
		self.response.write("Created team %s in league %s" % (self.request.get("name"), league.name))

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
		league = match.League.new_league(self.request.get("name"))
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

		match_key = m.put()

		for tk in team_keys:
			team = ndb.Key(urlsafe=tk).get()
			team.matches.append(match_key)
			team.put()

		refs = [ref.get() for ref in m.referees]
		teams = [team.get() for team in m.teams]

		template_values = {"match":m, "referees":refs, "teams":teams, "field":m.field.get()}
		template = JINJA_ENVIRONMENT.get_template('match.json')
		self.response.write(template.render(template_values))

class GetReferees(BaseHandler):
	def get(self):
		league_key = self.request.get("league")
		league = ndb.Key(urlsafe=league_key).get()
		
		refs = [ref.get() for ref in league.referees]

		template_values = {"referees":refs}
		template = JINJA_ENVIRONMENT.get_template('referee.json')
		self.response.write(template.render(template_values))

class GetTeams(BaseHandler):
	def get(self):
		league_key = self.request.get("league")
		league = ndb.Key(urlsafe=league_key).get()

		template_values = {"teams":league.teams}
		template = JINJA_ENVIRONMENT.get_template('teams.json')
		self.response.write(template.render(template_values))

class GetMatches(BaseHandler):
	def get(self):
		league_key = self.request.get("league")
		league = ndb.Key(urlsafe=league_key).get()
		
		matches = []

		for team in league.teams:
			matches.extend(team.get().matches)

		# Hack to remove duplicates for now
		matches = list(set(matches))

		template_values = {"matches":matches}
		template = JINJA_ENVIRONMENT.get_template('matches.json')
		self.response.write(template.render(template_values))



