import datetime
import hashlib
import os
import random
import string
import urllib2

from google.appengine.api import mail
from google.appengine.ext import ndb

import match

def register_new_person(name,email,password):

	if len(name) == 0:
		raise Exception("Name cannot be empty")
	elif len(email) == 0:
		raise Exception("Email cannot be empty")
	elif len(password) == 0:
		raise Exception("Password cannot be empty")
	
	new_person = ndb.Key(match.Person, email).get()
	if new_person is not None:
		raise Exception("Account with that email already exists")

	(password,salt) = salt_password(password)

	new_person = match.Person(id=email)
	new_person.populate(name=name, email=email, password=password, salt=salt)
	new_person.put()

	return new_person

def login_person(email,password):
	person_to_login = ndb.Key(match.Person, email).get()
	password = salt_password(password, person_to_login.salt)[0]

	if person_to_login.password == password:
		return person_to_login
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
