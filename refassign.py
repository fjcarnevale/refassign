import webapp2
import handlers

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

application = webapp2.WSGIApplication([
	('/', handlers.Index),
	('/add_team', handlers.AddTeam),
	('/add_ref', handlers.AddRef),
	('/add_field', handlers.AddField),
	('/add_match', handlers.AddMatch),
	('/add_league', handlers.AddLeague),
	('/dynamic/create_match.html', handlers.CreateMatch),
	('/dynamic/create_ref.html', handlers.CreateRef),
	('/dynamic/create_team.html', handlers.CreateTeam),
	('/get_referees', handlers.GetReferees)
], config=config, debug=True)






















