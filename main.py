import wsgiref.handlers
import httplib2
import jinja2
from google.appengine.api.memcache import Client
from google.appengine.ext import db
from google.appengine.api import users
import webapp2
import oauth2 as oauth
import time, os, simplejson
import urlparse

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

mem = Client()
http = httplib2.Http(mem)


consumer_key    =   'wecevzrnh0f3'
consumer_secret =   'bebASsugFs5IJfmV'
request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
access_token_url =  'https://api.linkedin.com/uas/oauth/accessToken'
authorize_url =     'https://api.linkedin.com/uas/oauth/authorize'

config = {"oauth_token_secret": "fbc2f385-3e90-4174-a6bb-23908d6f64ed", "oauth_authorization_expires_in": "0","oauth_token": "2f84a781-03ce-42f1-a845-0e9f8ccf5e34", "oauth_expires_in": "0"}
#config_data = {u'oauth_token_secret': 'fbc2f385-3e90-4174-a6bb-23908d6f64ed', u'oauth_authorization_expires_in': 0, u'oauth_token': '2f84a781-03ce-42f1-a845-0e9f8ccf5e34', u'oauth_expires_in': '0'}'
#config_file   = '.service.dat'

class FileModel(db.Model):
	blob = db.BlobProperty()


def get_auth():
		consumer = oauth.Consumer(consumer_key, consumer_secret)
		client = oauth.Client(consumer)

		#try:
		#	filehandle = open(config_file)
			
		# except IOError as e:
		# #	filehandle = open(config_file,"r")
		# 	print("We don't have a service.dat file, so we need to get access tokens!");
		# 	content = make_request(client,request_token_url,{},"Failed to fetch request token","POST")
		
		# 	request_token = dict(urlparse.parse_qsl(content))
		# 	print "Go to the following link in your browser:"
		# 	print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
		 
		# 	oauth_verifier = raw_input('What is the PIN? ')
		 
		# 	token = oauth.Token(request_token['oauth_token'],
		# 	request_token['oauth_token_secret'])
		# 	token.set_verifier(oauth_verifier)
		# 	client = oauth.Client(consumer, token)
		 
		# 	content = make_request(client,access_token_url,{},"Failed to fetch access token","POST")
			
		# 	access_token = dict(urlparse.parse_qsl(content))
		 
		# 	token = oauth.Token(
		# 		key=access_token['oauth_token'],
		# 		secret=access_token['oauth_token_secret'])
		 
		# 	client = oauth.Client(consumer, token)
		# 	#simplejson.dump(access_token,filehandle)

		# 	obj = FileModel()
		# 	obj.blob = db.Blob(simplejson.dump(access_token))

		
		# else:
			#config = simplejson.load(filehandle)
		#config = simplejson.JSONEncoder().encode(config_data)
		# config = simplejson.dumps(config_data)
		# print(config)
		# return config
		# #print(config['oauth_token_secret'])
		#config = config_data

		if ("oauth_token" in config and "oauth_token_secret" in config):
			token = 	oauth.Token(config['oauth_token'],
	    				config['oauth_token_secret'])
			client = oauth.Client(consumer, token)
		else:
			#print("We had a .service.dat file, but it didn't contain a token/secret?")
			exit()
		return client

	# Simple oauth request wrapper to handle responses and exceptions
def make_request(client,url,request_headers={},error_string="Failed Request",method="GET",body=None):
	if body:
		resp,content = client.request(url, method, headers=request_headers, body=body)
	else:
		resp,content = client.request(url, method, headers=request_headers)
	#print resp.status
		
	if resp.status >= 200 and resp.status < 300:
		return content
	elif resp.status >= 500 and resp.status < 600:
		error_string = "Status:\n\tRuh Roh! An application error occured! HTTP 5XX response received."
		log_diagnostic_info(client,url,request_headers,method,body,resp,content,error_string)
		
	else:
		status_codes = {403: "\n** Status:\n\tA 403 response was received. Usually this means you have reached a throttle limit.",
						401: "\n** Status:\n\tA 401 response was received. Usually this means the OAuth signature was bad.",
						405: "\n** Status:\n\tA 405 response was received. Usually this means you used the wrong HTTP method (GET when you should POST, etc).",
						400: "\n** Status:\n\tA 400 response was received. Usually this means your request was formatted incorrectly or you added an unexpected parameter.",
						404: "\n** Status:\n\tA 404 response was received. The resource was not found."}
		if resp.status in status_codes:
			#log_diagnostic_info(client,url,request_headers,method,body,resp,content,status_codes[resp.status])
			return status_codes[resp.status][1]
		else:
			#log_diagnostic_info(client,url,request_headers,method,body,resp,content,http_status_print[resp.status][1])
			#log_diagnostic_info(client,url,request_headers,method,body,resp,content,status_codes[resp.status][1])
			return status_codes[resp.status][1]

class ConnectionsJSON(webapp2.RequestHandler):

  	def get(self):
		client = get_auth()
  		#response = make_request(client,"http://api.linkedin.com/v1/people/~",{"x-li-format":'json'})
  		response = make_request(client,"http://api.linkedin.com/v1/people/~/connections?format=json")
		response = simplejson.loads(response)
		self.response.out.write(simplejson.dumps(response['values']))

class MainPage(webapp2.RequestHandler):		

    def get(self):
		client = get_auth()
		template_values = {'greetings': "hello"}
		template = jinja_environment.get_template('index.html')
  		#self.response.out.write('Time to build our app!')
  		self.response.out.write(template.render(template_values))
		# Simple profile call, returned in JSON


app = webapp2.WSGIApplication([
	('/', MainPage),
	('/persons', ConnectionsJSON)],
                              debug=True)