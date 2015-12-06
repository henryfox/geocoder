import webapp2
import os
import jinja2
from urllib import urlopen
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
		option = self.request.get("option")
		adress = self.request.get("adress")
		api_key_file = os.path.join(os.path.dirname(__file__), "secret.txt")
		api_key = open(api_key_file)
		api_key = api_key.read()
		if option == "geocode":
			info = urlopen("https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (adress, api_key))
		if option == "reverse-geocode":
			info = urlopen("https://maps.googleapis.com/maps/api/geocode/json?latlng=%s&key=%s" % (adress, api_key))
		info = info.read()
		j = json.loads(info)
		geometry = j["results"][0]["geometry"]["location"]
		if option == "geocode": 
			lat = geometry["lat"]
			lng = geometry["lng"]
		formated_adress = j["results"][0]["formatted_address"]
		if option == "geocode":
			self.render("response.html", title="response", lat=lat, lng=lng, adress=formated_adress)
		if option == "reverse-geocode":
			self.render("response_reverse.html", adress=formated_adress, title="response")

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/response', replyhandler),
], debug=True)