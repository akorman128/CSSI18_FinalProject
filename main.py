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

# class for user  object, had properties ID and points
class Account(ndb.Model):
    id = ndb.StringProperty()
    points = ndb.FloatProperty()

# class for Project object, has properties title, date, area, description and user_id
class Project(ndb.Model):
    title = ndb.StringProperty()
    date = ndb.DateProperty()
    area = ndb.StringProperty()
    description = ndb.StringProperty()
    user_id = ndb.StringProperty()

class UserProfileHandler(webapp2.RequestHandler):
    """ This is used for the "user profile" page"""
    def get(self):
        # Sign in was required, so get user info from Google App Engine
        user = users.get_current_user()
        nickname = user.nickname()
        logout_url = users.create_logout_url('/')
        greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(nickname, logout_url)

        # If no account exists, make one
        if len(Account.query(Account.id == user.user_id()).fetch()) == 0:
            # create user object
            new_user = Account(id = user.user_id(), points = 0)

            # update database and returns user key
            new_user_key = new_user.put()

        # Variables to pass into the user_profile.html page
        template_vars = {
            'nickname': nickname,
            'logout': logout_url,
            'logout_url': logout_url,
            'points': Account.query(Account.id == user.user_id()).fetch()[0].points
        }

        # render template
        profile_template = JINJA_ENVIRONMENT.get_template('templates/html/user_profile.html')
        # passes variable dictionary
        self.response.write(profile_template.render(template_vars))


        #calls handler on /create page
class CreateProjectHandler(webapp2.RequestHandler):
    def get(self):
        # renders create page
        create_template = JINJA_ENVIRONMENT.get_template('templates/html/create.html')
        self.response.write(create_template.render())

    def post(self):
        # Sign in was required, so get user info from Google App Engine
        user = users.get_current_user()
        nickname = user.nickname()

        current_user_account = Account.query(Account.id == user.user_id())
        print "Hello" + str(current_user_account.fetch(keys_only=True))
        current_user_key = current_user_account.fetch(keys_only=True)[0].string_id()

        # title = self.request.get('title')
        # date = self.request.get('date')
        # area = self.request.get('area')
        # description = self.request.get('description')

        #queries accounts to find kind object matching current user, fetches key
        current_user_account = Account.query(Account.id == user.user_id()).fetch(keys_only=True)[0].string_id()

        # creates new project object
        new_project = Project(title = self.request.get('title'), date = self.request.get('date'), area = self.request.get('area'), \
        description = self.request.get('description'), user_id = current_user_key )
        # new_project.title = title
        # new_project.date = date
        # new_project.area = area
        # new_project.description = description
        # new_project.user_id = current_user_key

        # returns key
        new_project_key = new_project.put()



#the route mapping
app = webapp2.WSGIApplication([
    #this line routes the main url ('/')  - also know as
    #the root route - to the Fortune Handler
    ('/user', UserProfileHandler),
    ('/create', CreateProjectHandler),
], debug=True)
