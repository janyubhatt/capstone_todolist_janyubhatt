import os
import re
import webapp2
import jinja2
import hashlib
import hmac
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__))
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)
SECRET = "secretcode"

class BaseHandler(webapp2.RequestHandler):
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
        
    def render_str(self,template, **params):
        template = jinja_environment.get_template(template)
        return template.render(params)    
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(BaseHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        visit_cookie_str = self.request.cookies.get("visits")
        if visit_cookie_str:
            cookie_val = self.check_secure_val(visit_cookie_str)
            if cookie_val:
                visits = int(cookie_val)

        visits +=1
        new_cookie_val = self.make_secure_val(str(visits))

        self.response.headers.add_header('Set-Cookie', 'visits=%s' %new_cookie_val)
        if visits > 10000:
            self.write('You are the best ever!')
        else:
            self.write("You've been here %s times" %visits)


    def hash_str(self,s):
        return hmac.new(SECRET, s).hexdigest()

    def make_secure_val(self,s):
        return "%s|%s" % (s,self.hash_str(s))

    def check_secure_val(self,h):
        val = h.split('|')[0]
        if h == self.make_secure_val(val):
            return val


app = webapp2.WSGIApplication([('/cookieapp', MainPage)], debug=True)