import datetime
import hashlib
import os
import random
import string
import urllib2

from google.appengine.api import mail
from google.appengine.ext import ndb

import match

def register_new_user(name,email,password):

	if len(name) == 0:
		raise Exception("Name cannot be empty")
	elif len(email) == 0:
		raise Exception("Email cannot be empty")
	elif len(password) == 0:
		raise Exception("Password cannot be empty")
	
	new_user = ndb.Key(match.User, email).get()
	if new_user is not None:
		raise Exception("User with that email already exists")

	(password,salt) = salt_password(password)

	new_user = match.User(id=email)
	new_user.populate(name=name, email=email, password=password, salt=salt, admin=match.Admin(), referee=match.Referee())
	new_user.put()

	return new_user

def login_user(email,password):
	user_to_login = ndb.Key(match.User, email).get()

	if user_to_login is None:
		raise Exception("Unrecognized email")

	password = salt_password(password, user_to_login.salt)[0]

	if user_to_login.password == password:
		return user_to_login
	else:
		raise Exception("Incorect password")


def salt_password(password, salt=None):
	if salt is None:
		salt = randomword(64)

	sha256 = hashlib.sha256()
	sha256.update(password + salt)
	password = sha256.hexdigest()

	return (password,salt)
	
	
def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))
