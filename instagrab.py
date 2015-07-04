import requests
import ConfigParser
from os.path import splitext,basename,isdir,isfile
from os import makedirs
#from pprint import pprint
import Queue
import threading
from urlparse import urlparse 

url = "https://api.instagram.com/v1/users/%s/feed?access_token=%s"
queue = Queue.Queue()
#instagram client for making requests
class Client:
	access_token = ""
	MAX = 10
	STATE_FILE = "state"
	base_url = "https://api.instagram.com/v1/users/%s/media/recent?access_token=%s"
	base_url_with_min_id = "https://api.instagram.com/v1/users/%s/media/recent?access_token=%s&min_id=%s"
	base_url_with_max_id = "https://api.instagram.com/v1/users/%s/media/recent?access_token=%s&max_id=%s"


	def __init__ (self, access_token,queue, MAX = 10):
		self.access_token = access_token
		self.queue = queue
		self.MAX = MAX

	def write_config(self,account_id,user_id,last_id):
		cfg = ConfigParser.RawConfigParser()
		cfg.add_section('data')
		cfg.set('data','user_id',user_id)
		if last_id:
			cfg.set('data','last_id',last_id)
		with open(account_id+'/'+self.STATE_FILE,'wb') as config_file:
			cfg.write(config_file)

	def smaller(self,id1,id2,l):
		return int(id1[0:-l])< int(id2[0:-l])

	def collect(self,account_id):
		cfg = ConfigParser.ConfigParser()
		user_id = 0
		last_id = None
		#try to get data in the folder
		if isdir(account_id):
			#load data file
			cfg.read(account_id+"/"+self.STATE_FILE)
			user_id = cfg.get('data','user_id')
			if cfg.has_option('data','last_id'):
				last_id = cfg.get('data','last_id')
		else:
			makedirs(account_id)
			user_id = self.retrieve_user_id(account_id)
		url = self.build_url(user_id,self.access_token,last_id)
		while (True):
			r = requests.get(url,verify='cacert.pem')
			resp = r.json()['data']
			for item in resp:
				if item['type'] == 'image':
					self.queue.put([item['images']['standard_resolution']['url'],account_id]) #queueing images to the downloading queue [link,account_id]
				#update latest image
				if (last_id == None):
					last_id = item['id']
				if (self.smaller(last_id,item['id'],len(user_id)+1)):
					last_id = item['id']
			#check for additional result	
			if not 'next_url' in r.json()['pagination']:
				break
			url = r.json()['pagination']['next_url']
		self.write_config(account_id,user_id,last_id)

	def build_url(self,user_id,access_token,min_id = None):
		if min_id:
			return self.base_url_with_min_id % (user_id,access_token,min_id)
		#normal request
		return self.base_url % (user_id,access_token)

	def retrieve_user_id(self,account_id):
		url = "https://api.instagram.com/v1/users/search?q=%s&access_token=%s&count=1"
		r = requests.get(url %(account_id,self.access_token),verify='cacert.pem')
		return r.json()['data'][0]['id']


#asynchoronous downloader
class Downloader(threading.Thread):
	def __init__(self,queue):
		threading.Thread.__init__(self)
		self.queue = queue

	def run(self):
		while True:
			target = self.queue.get()
			path = target[1]+"/"
			r = requests.get(target[0],stream=True,verify='cacert.pem')
			if r.status_code == 200:
				filename = splitext(basename(urlparse(target[0]).path))
				filename = filename[0] + filename[1]
				if not isfile(path+filename):
					with open(path + filename, 'wb') as f:
						for chunk in r.iter_content(1024):
							f.write(chunk)
			self.queue.task_done()


#main function 
def main(account_id):
	c = Client("206279665.74069ea.3e7744ba4dfd4d6384661e55ae69d5ed",queue)
	#generate downloader thread
	for i in range(3):
		 	t = Downloader(queue)
		 	t.setDaemon(True)
		 	t.start()
	#start collecting
	c.collect(account_id)
	#termination
	queue.join()



#collector
if __name__ == '__main__':
	main('xolovestephi')