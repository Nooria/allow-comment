
import os
from google.appengine.ext import ndb
import time
import jinja2
import webapp2



jinja_env = jinja2.Environment(
	loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
	autoescape=True)

#Generic key used to group Comments into an entitiy group
PARENT_KEY = ndb.Key("Entity","comment_root")

#This is object that will represent the Comments.
#We are using Object Oriented Programming to create objects in order to put 
#them in Google's Database .This object inherit Google ndb.Model class


class Comments(ndb.Model):
	"""Model object used to store Comments in the datastore"""
	name = ndb.StringProperty()
	comment = ndb.StringProperty()
	date = ndb.DateTimeProperty(auto_now_add=True)
   
#Ancestor Query, as shown , are strongly consistent with the high
#Replication Datastore. Query that span entitiy group are eventually consistent.

class ErrorPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_env.get_template("error.html")
		self.response.out.write(template.render())


		

class MainPage(webapp2.RequestHandler):
    
    def get(self):
        comment_query = Comments.query(ancestor = PARENT_KEY).order(-Comments.date)
        template = jinja_env.get_template("index.html")
        self.response.write(template.render({"comment_query": comment_query}))

 

class AddcommentAction(webapp2.RequestHandler):
	def post(self):
# We set the same parent kek on the 'Comments' to 
#ensure each Comments is in the same entitiy group.

		next_comment = Comments(parent=PARENT_KEY,
			                    name = self.request.get("name").strip(),
			                    comment = self.request.get("comment").strip())
		if not (next_comment.comment):
			self.redirect(self.request.referer)
			self.redirect("/error")
			
#Write to the Google Datastore
		else:
		    next_comment.put()
# here redirect and send it back to whoever send him here(referer)
		    self.redirect(self.request.referer)


app = webapp2.WSGIApplication([
	("/", MainPage),
	("/addcomment", AddcommentAction),
	("/error",ErrorPage)
	],debug = True)