import webapp2
import os
import jinja2
from urllib2 import *
import json

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape  = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.render("geocoder.html", title="geocoder")

class replyhandler(Handler):
	def get(self):
		self.adress = self.request.get("adress")
		api_key_file = os.path.join(os.path.dirname(__file__), "secret.txt")
		api_key = open(api_key_file)
		api_key = api_key.read()
		self.response.out.write(api_key)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/coords', replyhandler)
], debug=True)