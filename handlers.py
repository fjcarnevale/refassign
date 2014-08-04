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

import user_controller
import league_controller
import match

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
    

def get_logged_in_user(handler):
  email = handler.session.get('user_email', None)
  
  if email is None:
    return None
    
  return ndb.Key(match.User, email).get()


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
    if get_logged_in_user(self) is None:
      return self.redirect("/static/login.html")
    else:
      return self.redirect("/dynamic/landing_page.html")

class Register(BaseHandler):
  def get(self):
    email = self.request.get("email")
    password = self.request.get("password")
    name = self.request.get("name")
    
    try:
      new_user = user_controller.register_new_user(name,email,password)
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
      user = user_controller.login_user(email,password)
      self.session['user_email'] = user.email
      return self.redirect("/dynamic/landing_page.html")
    except Exception as e:
      self.response.write("Failed to login : %s" % str(e))

class Logout(BaseHandler):
  def get(self):
    self.session['user_email'] = None
    return self.redirect("/static/login.html")

class LandingPage(BaseHandler):
  def get(self):
    user = get_logged_in_user(self)

    template_values = {"user":user}
    template = JINJA_ENVIRONMENT.get_template('dynamic/landing_page.html')
    self.response.write(template.render(template_values))

class LeaguePage(BaseHandler):
  def get(self):
    league_key = self.request.get("league")
    league = ndb.Key(urlsafe = league_key).get()
    
    template_values = {"league":league}
    template = JINJA_ENVIRONMENT.get_template("dynamic/league_page.html")
    self.response.write(template.render(template_values))
    
class TeamPage(BaseHandler):
  def get(self):
    team_key = self.request.get("team")
    team = ndb.Key(urlsafe = team_key).get()
    
    template_values = {"team":team}
    template = JINJA_ENVIRONMENT.get_template("dynamic/team_page.html")
    self.response.write(template.render(template_values))
    

class RefereePage(BaseHandler):
  def get(self):
    user_key = self.request.get("user")
    user = ndb.Key(urlsafe = user_key).get()
    
    print "User has %d matches" % len(user.referee.matches)
    
    template_values = {"user":user}
    template = JINJA_ENVIRONMENT.get_template("dynamic/referee_page.html")
    self.response.write(template.render(template_values))

class AddLeague(BaseHandler):
  def get(self):
    user = get_logged_in_user(self)
    name = self.request.get("name")
    league = league_controller.create_new_league(self.request.get("name"), admins=[user])
    
    self.response.write("Created league %s" % league.name)
    
class AddTeam(BaseHandler):
  def get(self):
    league_key = ndb.Key(urlsafe = self.request.get("league"))
    league = league_key.get()

    team_key = league.add_new_team(self.request.get("name"))
    
    self.response.write("Created team %s in league %s" % (self.request.get("name"), league.name))
    
class AddField(BaseHandler):
  def get(self):
    league_key = ndb.Key(urlsafe = self.request.get("league"))
    league = league_key.get()
    
    name = self.request.get("name")
    location = self.request.get("location")
    
    field = league_controller.create_field(league, name, location)
    
    self.response.write("Created field %s in league %s" % (self.request.get("name"), league.name))
    
class AddReferee(BaseHandler):
  def get(self):
    league_key = ndb.Key(urlsafe = self.request.get("league"))
    league = league_key.get()
    
    email = self.request.get("email")
    user = ndb.Key(match.User, email).get()
    
    league_controller.add_referee_to_league(league,user)
    
    self.response.write("Added user %s as a referee for league %s" % (user.name, league.name))
    
class AddMatch(BaseHandler):
  def get(self):
    date = datetime.datetime.strptime(self.request.get("date"), "%Y-%m-%dT%H:%M")

    team_keys = self.request.get('team', allow_multiple=True)
    teams = [ndb.Key(urlsafe=team_key).get() for team_key in team_keys]
    
    field_key = self.request.get('field')
    field = ndb.Key(urlsafe=field_key).get()
    
    referee_keys = self.request.get('referee', allow_multiple=True)
    referees = [ndb.Key(urlsafe=referee_key).get() for referee_key in referee_keys]
    
    league_key = self.request.get('league')
    league = ndb.Key(urlsafe=league_key).get()

    match = league_controller.create_match(league, teams, date, referees, field)

    template_values = {"match":match}
    template = JINJA_ENVIRONMENT.get_template('match.json')
    self.response.write(template.render(template_values))
    
class CancelMatch(BaseHandler):
  def get(self):
    match_key = self.request.get("match")
    match = ndb.Key(urlsafe=match_key).get()
    
    league_controller.cancel_match(match)
    
    self.redirect(self.request.referrer)



