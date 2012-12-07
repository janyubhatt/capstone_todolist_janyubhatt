import webapp2

form="""
<form action="/testform">
    <input name="q">
    <input type="submit">
</form>
"""
class TestHandler(webapp2.RequestHandler):
  def get(self):
        q = self.request.get("q")
        self.response.out.write(q)
        
        #self.response.headers['Content-Type'] = 'text/plain'
        #self.response.out.write(self.request)

class MainPage(webapp2.RequestHandler):
  def get(self):
      #self.response.headers['Content-Type'] = 'text/plain'
      self.response.out.write(form)

app = webapp2.WSGIApplication([('/', MainPage),('/testform',TestHandler)],
                              debug=True)