import webapp2
import jinja2
import os
import random
import time
from datetime import datetime
from google.appengine.api import users
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

def getUserAccount():
    # Sign in was required, so get user info from Google App Engine
    user = users.get_current_user()
    nickname = user.nickname()
    logout_url = users.create_logout_url('/')
    greeting = 'Welcome, {}! (<a href="{}">sign out</a>)'.format(nickname, logout_url)

    # If no account exists, make one
    if len(Account.query(Account.id == user.user_id()).fetch()) == 0:
        # create user object
        new_user = Account(id = user.user_id(), points = 0, name = nickname)
        # update database and returns user key
        new_user_key = new_user.put()

    return user, nickname, logout_url, greeting


# class for user  object, had properties ID and points
class Account(ndb.Model):
    id = ndb.StringProperty()
    points = ndb.FloatProperty()
    name = ndb.StringProperty()

# class for Project object, has properties title, date, area, description and user_id
class Project(ndb.Model):
    title = ndb.StringProperty()
    date = ndb.DateProperty()
    area = ndb.StringProperty()
    description = ndb.StringProperty()
    user_id = ndb.StringProperty()
    time_requested = ndb.FloatProperty()

class WelcomeHandler(webapp2.RequestHandler):
    """ If user goes to the / domain, redirect to user profile """
    def get(self):
        self.redirect('/user')

class UserProfileHandler(webapp2.RequestHandler):
    def get(self):

        user, nickname, logout_url, greeting = getUserAccount()

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


class CreateProjectHandler(webapp2.RequestHandler):
    def get(self):
        logout_url = users.create_logout_url('/')
        template_vars ={
            'logout': logout_url
        }
        # renders create page
        create_template = JINJA_ENVIRONMENT.get_template('templates/html/create.html')
        self.response.write(create_template.render(template_vars))

    def post(self):
        user, nickname, logout_url, greeting = getUserAccount()

        # find user account that matches the current user's id
        current_user_account = Account.query(Account.id == user.user_id())
        # get the key id for that account
        current_user_key = str(current_user_account.fetch(keys_only=True)[0].id())

        # parse the input date into Python DateTime format
        new_date = datetime.strptime(self.request.get('date'), '%m/%d/%Y')

        # creates new project object
        new_project = Project(title = self.request.get('title'), area = self.request.get('area'), \
        description = self.request.get('description'), date = new_date, user_id = current_user_key )

        # save the new project into the database and return its key
        new_project_key = new_project.put()
        # redirect to "project view" while passing in project key id
        self.redirect('/projectview?id=' + str(new_project_key.id()))


class ProjectViewHandler(webapp2.RequestHandler):
    def get(self):
        user, nickname, logout_url, greeting = getUserAccount()

        #  gets id of current_project_id
        current_project_id = int(self.request.get('id'))
        # returns project w/ current project's id
        current_project = Project.get_by_id(current_project_id)

        #get project owner id
        owner_id = int(current_project.user_id)
        # gets owner object
        owner = Account.get_by_id(owner_id)

        # Variables to pass into the project-view.html page
        template_vars = {
            'project_title' : current_project.title,
            'area' : current_project.area,
            'date' : current_project.date,
            'description': current_project.description,
            'owner' : owner.name+' ',

                #
                # 'nickname': nickname,
                # 'logout': logout_url,
                # 'points': Account.query(Account.id == user.user_id()).fetch()[0].points
            }

            # render template
        profile_template = JINJA_ENVIRONMENT.get_template('templates/html/project-view.html')
        # passes variable dictionary
        self.response.write(profile_template.render(template_vars))

class ExploreQueryHandler(webapp2.RequestHandler):
    def get(self):
        user, nickname, logout_url, greeting = getUserAccount()

        # gets list of project
        list_projects = Project.query().fetch()
        print(list_projects)

        template_vars = {
            'list_projects' : list_projects,
        }

        # render template
        profile_template = JINJA_ENVIRONMENT.get_template('templates/html/explore-projects.html')
        # passes variable dictionary
        self.response.write(profile_template.render(template_vars))

    def post(self):
        # gets area defined in selector in html
        area = self.request.get('area')
        # if area == all, set list_projects to all projects in db
        if (area == 'all'):
            list_projects = Project.query().fetch()
            print(list_projects)
        else:
        # else only show projects specified with area selected
            list_projects = Project.query(Project.area == area).fetch()
            print(list_projects)

        template_vars = {
            'list_projects' : list_projects,
        }
        profile_template = JINJA_ENVIRONMENT.get_template('templates/html/explore-projects.html')
        self.response.write(profile_template.render(template_vars))



#the route mapping
app = webapp2.WSGIApplication([
    #this line routes the main url ('/')  - also know as
    #the root route - to the Fortune Handler
    ('/', WelcomeHandler),
    ('/user', UserProfileHandler),
    ('/create', CreateProjectHandler),
    ('/explore', ExploreQueryHandler),
    ('/projectview', ProjectViewHandler)
], debug=True)
