import os
import re
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
class BlogPost(db.Model):
    subject=db.StringProperty()
    content=db.TextProperty()
    created=db.DateTimeProperty(auto_now_add=True)
class MainPage(BaseHandler):
    def render_main(self):
        blogs=db.GqlQuery("Select * From BlogPost Order By created Desc")
        self.render('/templates/blog.html', blogs=blogs)
    def get(self):
        self.render_main()

class NewEntry(BaseHandler):
    def render_entrypage(self, subject="",content="",error=""):
        self.render('/templates/newblog.html',subject = subject,content=content,error=error)
        
    def get(self):
        self.render_entrypage()
    def post(self):
        subject = self.request.get('subject')
        content= self.request.get('content')
        
        if subject and content:
            blogpost=BlogPost(subject=subject, content=content)
            blogpost.put()
            blog_id = str(blogpost.key().id())
            self.redirect('/blog/' + blog_id)
        else: 
            error="Entries need to have both subject and blog post"
            self.render_entrypage(subject,content,error)

class EntryPage(BaseHandler):
    def get(self,blog_id):
        blog = BlogPost.get_by_id(int(blog_id))
        self.render('templates/entrypost.html', blog=blog)
        
app = webapp2.WSGIApplication([('/blog', MainPage),
                                ('/blog/newpost', NewEntry),
                                ('/blog/(\d+)', EntryPage)], debug=True)