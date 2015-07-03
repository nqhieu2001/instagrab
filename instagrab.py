import requests
import ConfigParser
from os.path import splitext,basename,isdir,isfile
from os import makedirs
from pprint import pprint

url = "https://api.instagram.com/v1/users/%s/feed?access_token=%s"

class Client:
	access_token = ""
	MAX = 10
	STATE_FILE = "state"
	base_url = "https://api.instagram.com/v1/users/%s/media/recent?access_token=%s"
	base_url_with_min_id = "https://api.instagram.com/v1/users/%s/media/recent?access_token=%s&min_id=%s"
	base_url_with_max_id = "https://api.instagram.com/v1/users/%s/media/recent?access_token=%s&max_id=%s"


	def __init__ (self, access_token, MAX = 10):
		self.access_token = access_token
		self.MAX = MAX

	def collect(self,account_id):
		cfg = ConfigParser.ConfigParser()
		user_id = 0
		max_id = None
		min_id = None
		#try to get data in the folder
		if isdir(account_id):
			#load data file
			cfg.read(account_id+"/"+self.STATE_FILE)
			user_id = cfg.get('data','user_id')
			if cfg.has_option('data','max-id'):
				max_id = cfg.get('data','max_id')
		else:
			user_id = self.retrieveUserID(account_id)
		url = self.buildUrl(user_id,self.access_token,max_id,min_id)
		#print url
		r = requests.get(url)
		resp = r.json()['data']
		for item in resp:
			if item['type'] == 'image':
				print item['images']['standard_resolution']['url'],
				print " from ",
				print item['user']['username']
		url = r.json()['pagination']['next_url']


	def buildUrl(self,user_id,access_token,max_id = None,min_id = None):
		if min_id:
			return self.base_url_with_min_id % (user_id,access_token,min_id)
		if max_id:
			return self.base_url_with_max_id % (user_id,access_token,max_id)
		#normal request
		return self.base_url % (user_id,access_token)

	def retrieveUserID(self,account_id):
		return 1


c = Client("206279665.74069ea.3e7744ba4dfd4d6384661e55ae69d5ed")
c.collect("xolovestephi")