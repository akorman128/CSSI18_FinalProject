import webapp2
import jinja2
import os
import random
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Account(ndb.Model):
    id = ndb.StringProperty()
    points = ndb.FloatProperty()

class UserProfileHandler(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        nickname = user.nickname()
        logout_url = users.create_logout_url('/')
        greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(nickname, logout_url)

        if len(Account.query(Account.id == user.user_id()).fetch()) == 0:
            new_user = Account()
            new_user.id = user.user_id()
            new_user.points = 0
            new_user_key = new_user.put()

        template_vars = {
            'nickname': nickname,
            'logout': logout_url,
            'greeting': greeting,
            'points': Account.query(Account.id == user.user_id()).fetch()[0].points
        }

        profile_template = JINJA_ENVIRONMENT.get_template('templates/html/user_profile.html')
        self.response.write(profile_template.render(template_vars))


    def post(self):
        pass
#the route mapping
app = webapp2.WSGIApplication([
    #this line routes the main url ('/')  - also know as
    #the root route - to the Fortune Handler
    ('/user', UserProfileHandler),
], debug=True)
