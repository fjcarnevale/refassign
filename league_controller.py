import datetime
import hashlib
import os
import random
import string
import urllib2

from google.appengine.api import mail
from google.appengine.ext import ndb

import match

def create_new_league(name, admins=[], assigners=[], referees=[], teams=[]):
    league = match.League()
    admin_keys = [admin.key for admin in admins]
    league.populate(name=name, admins=admin_keys, assigners=assigners, referees=referees, teams=teams)
    league_key = league.put()
    
    for user in admins:
      if user.admin is None:
        user.admin = match.Admin()
        
      user.admin.leagues.append(league_key)
      user.put()
    
    return league
    
def create_match(league, teams, date, referees=[], field=None):
  new_match = match.Match()
  new_match.populate(date=date, teams=[team.key for team in teams], referees=referees, field=field.key)
  match_key = new_match.put()
  
  league.matches.append(match_key)
  league.put()
  
  for team in teams:
    team.matches.append(match_key)
    team.put()
  
  return new_match
  
def create_field(league, name, location):
  new_field = match.Field()
  new_field.populate(name=name, location=location)
  new_field_key = new_field.put()
  
  league.fields.append(new_field_key)
  league.put()
  
  return new_field
  
def add_referee_to_league(league, user):
  league.referees.append(user.key)
  league.put()
  
  if user.referee is None:
    user.referee = match.Referee()
    user.referee.grade = 0
    
  user.referee.leagues.append(league.key)
  user.put()
  