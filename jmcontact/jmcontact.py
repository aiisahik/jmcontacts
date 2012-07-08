import pdb
import oauth2 as oauth
import httplib2
import time, os, simplejson
import urlparse
import BaseHTTPServer 
from xml.etree import ElementTree as ET
# TODO Add your own consumer key and secret
consumer_key    =   'wecevzrnh0f3'
consumer_secret =   'bebASsugFs5IJfmV'
 
# the URLs we will use
request_token_url = 'https://api.linkedin.com/uas/oauth/requestToken'
access_token_url =  'https://api.linkedin.com/uas/oauth/accessToken'
authorize_url =     'https://api.linkedin.com/uas/oauth/authorize'
 
# Create our OAuth consumer instance
consumer = oauth.Consumer(consumer_key, consumer_secret)
client = oauth.Client(consumer)
 
# make_request is a simple wrapper around the oauth request call
# It is essentially the code below (but is detailed in full later + in the code download)
# make_request(client,url,request_headers={},error_string="Failed Request",method="GET",body=None)
#      resp,content = client.request(url, method, headers=request_headers, body=body)
content = make_request(client,request_token_url,{},"Failed to fetch request token","POST")
 
# parse out the tokens from the response
request_token = dict(urlparse.parse_qsl(content))
print "Go to the following link in your browser:"
print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
 
# ask for the verifier pin code
oauth_verifier = raw_input('What is the PIN? ')
 
# swap in the new token + verifier pin
token = oauth.Token(request_token['oauth_token'],
request_token['oauth_token_secret'])
token.set_verifier(oauth_verifier)
client = oauth.Client(consumer, token)
 
# fetch the access token
content = make_request(client,access_token_url,{},"Failed to fetch access token","POST")
 
# parse out the access token
access_token = dict(urlparse.parse_qsl(content))
 
# swap in the new auth token to the client
token = oauth.Token(
    key=access_token['oauth_token'],
    secret=access_token['oauth_token_secret'])
client = oauth.Client(consumer, token)
 
# Simple profile call
print "\n********A basic user profile call********"
response = make_request(client,"http://api.linkedin.com/v1/people/~")
print response