import webapp2
import handlers

config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-super-secret-key',
}

application = webapp2.WSGIApplication([
	('/', handlers.Index),
	('/register', handlers.Register),
	('/login', handlers.Login),
	('/logout',handlers.Logout),
	('/dynamic/landing_page.html', handlers.LandingPage),
	('/add_team', handlers.AddTeam),
	('/add_ref', handlers.AddRef),
	('/add_field', handlers.AddField),
	('/add_match', handlers.AddMatch),
	('/add_league', handlers.AddLeague),
	('/dynamic/create_match.html', handlers.CreateMatch),
	('/dynamic/create_ref.html', handlers.CreateRef),
	('/dynamic/create_team.html', handlers.CreateTeam),
	('/dynamic/view_matches.html', handlers.ViewMatches),
	('/dynamic/view_leagues.html', handlers.ViewLeagues),
	('/dynamic/league_page.html', handlers.ViewLeague),
	('/get_referees', handlers.GetReferees),
	('/get_matches', handlers.GetMatches),
	('/get_teams', handlers.GetTeams)
], config=config, debug=True)






















