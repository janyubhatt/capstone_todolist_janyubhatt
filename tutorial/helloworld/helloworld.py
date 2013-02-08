import webapp2
import cgi
import string
import re
import jinja2
import os
from google.appengine.ext import db
import hashlib
import hmac
import random

#This is the secret password used to create salts
SECRET = "jessepinkman"

#Initializes template features from jinja2 framweworkd
template_dir = os.path.join(os.path.dirname(__file__))
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
      
                               autoescape = True)



welcome="""
<h1>Welcome %s<h1>
"""



class MainPage(webapp2.RequestHandler):
    
    months = ['January',
          'February',
          'March',
          'April',
          'May',
          'June',
          'July',
          'August',
          'September',
          'October',
          'November',
          'December']
    
    def valid_month(self,month):
        if month:
            cap_month = month.capitalize()
            if cap_month in self.months:
                return cap_month
    
    def valid_day(self,day):
        if day and day.isdigit():
            num_day = int(day)
            if num_day >0 and num_day <=31:
                return num_day
    
    def valid_year(self,year):
        if year and year.isdigit():
            year = int(year)
            if year > 1900  and year < 2020:
                return year
                
    def write_form(self, error="", month="", day="", year=""):
        template_values={'error': error,
                         'month': self.escape_html(month),
                         'day': self.escape_html(day),
                         'year': self.escape_html(year)}
        template = jinja_environment.get_template('templates/helloworld.html')
        self.response.out.write(template.render(template_values))

    def get(self):
        self.write_form()

    def post(self):
        user_month = self.request.get("month")
        user_day = self.request.get('day')
        user_year = self.request.get('year')
        
        month = self.valid_month(self.request.get("month"))
        day = self.valid_day(self.request.get('day'))
        year = self.valid_year(self.request.get('year'))
        
        if not (month and day and year):
            self.write_form("Invalid BirthDay", user_month, user_day, user_year)
        else:
            self.redirect("/thanks")
    def escape_html(self, s):
        return cgi.escape(s, quote=True)



class ThanksHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("Thanks that's a totally valid Birtday")
class Rot13Handler(webapp2.RequestHandler):
    def write_self(self,cipher=""):
        template = jinja_environment.get_template('templates/rot13.html')
        self.response.out.write(template.render({'cipher':cipher}))
    
    def get(self):
        self.write_self()
        
    def post(self):
        rot13=''
        entered = self.request.get('text')
        if entered:
            rot13=entered.encode('rot13')
        self.write_self(rot13)
        
        
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)


def make_salt():
      return ''.join(random.choice(string.letters) for x in xrange(5))

def make_hash(pw,salt=None):
  if not salt:
    salt = make_salt()
  tohash = salt + SECRET + str(pw)  
  #h = hashlib.sha256(tohash).hexdigest()
  h= hmac.new(str(salt+SECRET),str(pw),hashlib.sha256).hexdigest()
  return '%s|%s' % (salt,h)



def valid_hash(pw, h):
      salt = h.split("|")[0]
      hashed = make_hash(pw,salt)
      if h == hashed:
          return True


class SignupPage(webapp2.RequestHandler):
    def write_self(self,template_values):
        template=jinja_environment.get_template('templates/signup.html')
        self.response.out.write(template.render(template_values))
    def get(self):
        template_values= {'username':"",
                         'password':"",
                         'verifypass':"",
                         'email':"",
                         'error_username':"",
                         'error_password':"",
                         'error_verify':"",
                         'error_email':""}
        self.write_self(template_values)

    def post(self):
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verifypass')
        email = self.request.get('email')

        params = {'username' : username,
                      'email' : email,
                      'error_username':"",
                      'error_password' : "",
                      'error_verify' : "",
                      'error_email' : ""}
        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.write_self(params)
        else:
          user_id_hash = self.register_user(username,password,email)
          if user_id_hash:
            self.response.headers.add_header("Set-Cookie", "user_id = %s; Path = /" %user_id_hash)
            self.redirect('/welcome')
          else:
            params['error_username'] = "This User already exists"
            self.write_self(params)

    def register_user(self,username,password,email=None):
      pass_hash = make_hash(password,username)
      user_account = UserAccount(username=username, password = pass_hash,email = email)
      matchingAccount = UserAccount.all()
      matchingAccount =matchingAccount.filter('username',user_account.username)
      if not (matchingAccount.count()>0):
        user_account.put()
        user_id = user_account.key().id()
        user_id_hash = make_hash(user_id, str(user_id))
        return user_id_hash
      else:
        return None  

class UserAccount(db.Model):
  username = db.StringProperty()
  password = db.StringProperty()
  email = db.StringProperty()




class WelcomePage(webapp2.RequestHandler): 
  def get(self):
    user_id_cookie_str = self.request.cookies.get("user_id")
    if user_id_cookie_str:
      user_id = int(user_id_cookie_str.split("|")[0])
      if valid_hash(user_id, user_id_cookie_str):
        user = UserAccount.get_by_id(user_id)
        username = user.username
        self.response.out.write("Welcome %s" %username)
      else:
        self.redirect("/signup")
        

class LoginHandler(webapp2.RequestHandler):
  def write_self(self,template_values):
        template=jinja_environment.get_template('templates/login.html')
        self.response.out.write(template.render(template_values))

  def get(self):
        template_values= {'loguser':"",
                         'logpass':"",
                         'error_loguser':"",
                         'error_logpass':""}
        self.write_self(template_values)

def post(self):
    username = self.request.get("username")
    password = self.request.get("password")
    pass_hashed = make_hash(password,username)

    matchingPass = UserAccount.all()
    matchinPass = matchingPass.filter('password',pass_hashed)

    haveError = False
    params = {'loguser':"",
              'logpass':"",
              'error_loguser':"",
              'error_logpass':""}
    if(matchingPass.count()==1):
        user = matchingPass.get()
        if (username == user.username):
            user_id = user.key().id()
            user_id_hash = make_hash(user_id, str(user_id))
            self.response.headers.add_header("Set-Cookie", "user_id = %s; Path = /" %user_id_hash)
            self.redirect('/welcome')
        else:
          haveError = True
    else:
      haveError=True


    if haveError:
        params['error_loguser'] = "username does not match password"
        params['loguser'] = username
        self.write_self(params)






app = webapp2.WSGIApplication([('/', MainPage),
                               ('/thanks', ThanksHandler),
                               ('/hwrot13', Rot13Handler),
                               ('/signup', SignupPage),
                               ('/welcome', WelcomePage),
                               ('/login', LoginHandler)], debug=True)
