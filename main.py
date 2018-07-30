import webapp2
import jinja2
import os
import random

#remember, you can get this by searching for jinja2 google app engine
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class ___Handler(webapp2.RequestHandler):
    def get(self):
        results_template = JINJA_ENVIRONMENT.get_template('templates/______.html')
        self.response.write(results_template.render())
    #add a post method
    #def post(self):
    def post(self):

        template_vars = {

        }

        results_template = JINJA_ENVIRONMENT.get_template('templates/_______.html')
        self.response.write(results_template.render(template_vars))

#the route mapping
app = webapp2.WSGIApplication([
    #this line routes the main url ('/')  - also know as
    #the root route - to the Fortune Handler
    ('/', _____),
    ('/_____', ___Handler),
], debug=True)
