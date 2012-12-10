import webapp2
import cgi
from string import letters
form = """
<form method="post">
    What is your birthday?
    <br>
    <label>
        Month
        <input type="text" name="month" value="%(month)s">
    </label>
    <label>
        Day
        <input type="text" name="day" value="%(day)s">
    </label>
    <label>
        Year
        <input type="text" name="year" value="%(year)s">
    </label>
    <div style="color: red">%(error)s</div>
    <br><br>
    <input type="submit">
</form>
<br>
<a href="/hwrot13">Rot13 homework page</a>
"""

rot = """
<h1> Enter some text to Rot13</h1>
<form method="post">
    <textarea name = "text" cols="50" rows="5">%(cipher)s</textarea>
    <input type="submit">
</form>
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
        self.response.out.write(form %{"error": error,
                                       "month": self.escape_html(month),
                                       "day": self.escape_html(day),
                                       "year": self.escape_html(year)})

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
        self.response.out.write(rot %{"cipher": cipher})
    
    def get(self):
        self.write_self()
        
    def post(self):
        rot13=''
        entered = self.request.get('text')
        if entered:
            rot13=entered.encode('rot13')
        self.response.out.write(rot %{'cipher': rot13})
        
        
app = webapp2.WSGIApplication([('/', MainPage),
                               ('/thanks', ThanksHandler),
                               ('/hwrot13', Rot13Handler)], debug=True)
