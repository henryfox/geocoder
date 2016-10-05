import webapp2
import os
import jinja2
from urllib import urlopen
import json
from google.appengine.ext import db
import logging
import os

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

class Data(db.Model):
	adress = db.StringProperty()
	gps = db.StringProperty()
	grg = db.StringProperty()
	ip = db.StringProperty()

class replyhandler(Handler):
	def get(self):
		ip = os.environ["REMOTE_ADDR"]
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
			data = Data(adress=formated_adress, gps=str(lat) + ", " + str(lng), grg="geocode", ip=ip)
			data.put()
		if option == "reverse-geocode":
			self.render("response_reverse.html", adress=formated_adress, title="response")
			data = Data(adress=formated_adress, gps=adress, grg="reverse geocode", ip=ip)
			data.put()


class api(webapp2.RequestHandler):
	def get(self):
		option = self.request.get("option")
		adress = self.request.get("loc")
		api_key_file = os.path.join(os.path.dirname(__file__), "secret.txt")
		api_key = open(api_key_file)
		api_key = api_key.read()
		if option == "geocode":
			info = urlopen("https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s" % (adress, api_key))
		if option == "reverse":
			info = urlopen("https://maps.googleapis.com/maps/api/geocode/json?latlng=%s&key=%s" % (adress, api_key))
		info = info.read()
		j = json.loads(info)
		geometry = j["results"][0]["geometry"]["location"]
		if option == "geocode": 
			lat = geometry["lat"]
			lng = geometry["lng"]
		formated_adress = j["results"][0]["formatted_address"]
		if option == "geocode":
			self.response.out.write(str(lat) + "," + str(lng))
		if option == "reverse":
			self.response.out.write(formated_adress)


class dataHandler(Handler):
	def get(self):
		try:
			password = self.request.cookies.get('password')
			if password == "my+name+is+jeff":
				password = "my name is jeff"
			else:
				password = self.request.get("password")
		except:
				password = self.request.get("password")

		if password == "my name is jeff":
			self.query = Data.all()
			try:
				i = self.query[0].adress
			except:
				self.response.out.write("no data")
			else:
				self.render("data.html", query=self.query, title="data")
				self.response.headers.add_header('Set-Cookie', 'password=my+name+is+jeff')
		else:
			self.response.out.write("that password is rong <a href='/login'><button>try agen</button></a>")

class loginHandler(Handler):
	def get(self):
		try:
			password = self.request.cookies.get('password')
			if password == "my+name+is+jeff":
				self.redirect("/db?password=my+name+is+jeff")
			else:
				self.render("login.html")
		except:
			self.render("login.html")

class deletHandler(Handler):
	def get(self):
		try:
			password = self.request.cookies.get('password')
			if password == "my+name+is+jeff":
				db.delete(Data.all(keys_only=True))
				self.redirect("/login")
			else:
				self.redirect("/login")
		except:
			self.redirect("/login")

class logoutHandler(Handler):
	def get(self):
		self.response.headers.add_header("Set-Cookie", 'password=none')
		self.redirect("/login")

class analiticsHandler(Handler):
	def get(self):
		li = []
		users = 0
		try:
			password = self.request.cookies.get('password')
			if password == "my+name+is+jeff":
				self.data = Data.all()
				for x in self.data:
					info = x.ip
					li.append(info)
					for y in li:
						if y == info:
							users += 1
				self.response.out.write(users)
			else:
				self.response.out.write("that password is rong <a href='/login'><button>try agen</button></a>")
		except:
			self.response.out.write("that password is rong <a href='/login'><button>try agen</button></a>")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/response', replyhandler),
    ('/api', api),
    ('/db', dataHandler),
    ('/login', loginHandler),
    ('/delete', deletHandler),
    ('/logout', logoutHandler),
    ('/analitics', analiticsHandler)
], debug=True)