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
  ('/dynamic/league_page.html', handlers.LeaguePage),\
  ('/dynamic/team_page.html', handlers.TeamPage),
  ('/add_league', handlers.AddLeague),
  ('/add_team', handlers.AddTeam),
  ('/add_field', handlers.AddField),
  ('/add_match', handlers.AddMatch)
], config=config, debug=True)






















