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


# one-to-many relationship with Project; one-to-many relationship with Donation
class Account(ndb.Model):
    id = ndb.StringProperty()
    points = ndb.FloatProperty()
    name = ndb.StringProperty()

# many-to-one relationship with Account; one-to-many relationship with Donation
class Project(ndb.Model):
    title = ndb.StringProperty()
    date = ndb.DateProperty()
    area = ndb.StringProperty()
    description = ndb.StringProperty()
    user_id = ndb.StringProperty()
    time_requested = ndb.FloatProperty()

# many-to-one relationship with Project; many-to-one relationship with Account
class Donation(ndb.Model):
    user_id = ndb.StringProperty()
    nickname = ndb.StringProperty()
    project_id = ndb.StringProperty()

class WelcomeHandler(webapp2.RequestHandler):
    """ If user goes to the / domain, redirect to user profile """
    def get(self):
        self.redirect('/user')

class UserProfileHandler(webapp2.RequestHandler):
    def get(self):

        user, nickname, logout_url, greeting = getUserAccount()

        # Find all the projects & donations belonging to the current user
        current_user_id = str(user.user_id())
        list_projects = Project.query(Project.user_id == current_user_id).fetch()
        list_donations = Donation.query(Donation.user_id == current_user_id).fetch()

        donation_time = {}
        donation_area = {}
        donation_title = {}
        donation_date = {}
        for donation in list_donations:
            project_id = donation.project_id

            hours = Project.query(Project.id == project_id).fetch().time_requested
            area = Project.query(Project.id == project_id).fetch().area
            project_title = Project.query(Project.id == project_id).fetch().title
            date = Project.query(Project.id == project_id).fetch().date

            donation_time[donation] = hours
            donation_area[donation] = area
            donation_title[donation] = project_title
            donation_date[donation] = date


        # Variables to pass into the user_profile.html page
        template_vars = {
            'nickname': nickname,
            'logout': logout_url,
            'logout_url': logout_url,
            'points': Account.query(Account.id == user.user_id()).fetch()[0].points,
            'list_projects': list_projects,
            'list_donations': list_donations,
            'donation_time': donation_time,
            'donation_area': donation_area,
            'donation_title': donation_title,
            'donation_date': donation_date,
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
        #current_user_account = Account.query(Account.id == user.user_id())
        # get the key id for that account
        #current_user_key = str(current_user_account.fetch(keys_only=True)[0].id())
        current_user_id = str(user.user_id())

        # parse the input date into Python DateTime format
        new_date = datetime.strptime(self.request.get('date'), '%Y-%m-%d')

        # creates new project object
        new_project = Project(title = self.request.get('title'), area = self.request.get('area'), \
        description = self.request.get('description'), date = new_date, user_id = current_user_id, \
        time_requested = float(self.request.get('time_requested')))

        # save the new project into the database and return its key
        new_project_key = new_project.put()
        # redirect to "project view" while passing in project key id
        self.redirect('/projectview?id=' + str(new_project_key.id()))

#******************************
class ProjectViewHandler(webapp2.RequestHandler):
    def get(self):
        user, nickname, logout_url, greeting = getUserAccount()

        #--------------------------
        # gets id of current_project_id
        current_project_id = int(self.request.get('id'))
        # returns project w/ current project's id
        current_project = Project.get_by_id(current_project_id)
        #--------------------------
        # get project owner id
        owner_id = str(current_project.user_id)
        # gets owner object
        owner_account = Account.query(Account.id == owner_id).fetch()[0]

        donation_list = Donation.query(Donation.project_id == str(current_project_id)).fetch()

        # Variables to pass into the project-view.html page
        template_vars = {
            'current_project_id' : current_project_id,
            'project_title' : current_project.title,
            'area' : current_project.area,
            'date' : current_project.date,
            'description': current_project.description,
            'owner' : str(owner_account.name),
            'request' : current_project.time_requested,
            #------------viewer info--------------
            'donation_list' : donation_list,
                #
                # 'nickname': nickname,
                # 'logout': logout_url,
                # 'points': Account.query(Account.id == user.user_id()).fetch()[0].points
            }

            # render template
        profile_template = JINJA_ENVIRONMENT.get_template('templates/html/project-view.html')
        # passes variable dictionary
        self.response.write(profile_template.render(template_vars))

    def post(self):
        user, nickname, logout_url, greeting = getUserAccount()
        # get current user object
        user_object = Account.query(Account.id == user.user_id()).fetch()[0]
        user_id = str(user.user_id())

        current_project_id = int(self.request.get('id'))
        current_project = Project.get_by_id(current_project_id)
        #current_project = Project.get_by_id(current_project_id).fetch()

        owner_id = str(current_project.user_id)
        #owner = Account.get_by_id(owner_id)
        owner_account = Account.query(Account.id == owner_id).fetch()[0]

        #--------------------------
        new_donation = Donation(user_id = str(user_id), project_id = str(current_project_id), nickname = nickname)
        new_donation_key = new_donation.put()
        donation_list = Donation.query(Donation.project_id == str(current_project_id)).fetch()

        # Variables to pass into the project-view.html page
        template_vars = {
            'current_project_id' : current_project_id,
            'project_title' : current_project.title,
            'area' : current_project.area,
            'date' : current_project.date,
            'description': current_project.description,
            'owner' : str(owner_account.name),
            'request' : current_project.time_requested,
            #------------viewer info--------------
            'donation_list' : donation_list,

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
        withdrawal = self.request.get('withdrawal')

        # if area == all and withdrawal == all, set list_projects to all projects in db
        if (area == 'all' and withdrawal == 'all'):
            list_projects = Project.query().fetch()
            print(list_projects)
        # if area is some other value than all, make an area specific query
        elif (area != 'all' and withdrawal == 'all'):
            list_projects = Project.query(Project.area == area).fetch()
        # if withdrawal is some other value than all, make a withdrawal specific query
        elif (area == 'all' and withdrawal != 'all'):
            withdrawal_float = float(self.request.get('withdrawal'))
            list_projects = Project.query(Project.time_requested == withdrawal_float).fetch()
        else:
        # if both the area and withdrawal are being queried
            withdrawal_float = float(self.request.get('withdrawal'))
            list_projects = Project.query(Project.area == area and Project.time_requested == withdrawal_float).fetch()
        #if nothing in list make an error message. at this point nothing happens with it
            if not list_projects:
                error_message = 'No matching time withdrawals.'
            print(list_projects)



        template_vars = {
            # 'error' : error_message,
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
