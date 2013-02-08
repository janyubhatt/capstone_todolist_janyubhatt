import os
import webapp2
import jinja2

from google.appengine.ext import db


template_dir = os.path.join(os.path.dirname(__file__))
jinja_environment = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)


class BaseHandler(webapp2.RequestHandler):
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
        
        
    def render_str(self,template, **params):
        template = jinja_environment.get_template(template)
        return template.render(params)    
    
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Artwork(db.Model):
    title=db.StringProperty(required = True)
    art = db.TextProperty(required= True)
    created = db.DateTimeProperty(auto_now_add=True)
         
    
class MainPage(BaseHandler):
    def render_main(self,title="",art="",error=""):
        arts =  db.GqlQuery("Select * from Artwork Order By created Desc")
        self.render('/templates/asciichan.html',title = title, art = art, arts=arts, error = error)
        
    def get(self):
        self.render_main()
        
    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')
        
        if title and art:
            a = Artwork(title=title, art=art)
            a.put()
            self.redirect('/asciichan')
        else:
            error="Please Fill out both fields"
            self.render_main(title,art,error)
    
app = webapp2.WSGIApplication([("/asciichan",MainPage)
                              ], debug=True)