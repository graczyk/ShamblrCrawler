
# for the API Fetch
import urllib.request
import json
import sys

# for the socket check
import socket
import random
import time

# the tumblr api key
my_api_key = "GVL9W0CL6PlLFo4WX1PiL541vsRngVpa7CRBsKClp0maIK3lie"


#get a new blog from the frontier
def get_blog_from_frontier(host,port):
	#connect to the frontier to get a socket to communicate with
	connection_success = False
	connection_success_fails = 0
	while not connection_success:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((host, port))
			connection_success = True
		except Exception as e:
			print("Could Not Link To Socket " + str(port))
			connection_success_fails += 1
			if connection_success_fails > 5:
				print("Max Link Fails to socket " + str(port))
				return False,None
			time.sleep(random.randrange(.1,.5))
			pass

	#send the json request for a socket
	s.send(str.encode(json.dumps({"request_type":"socket_request"})))
	s.shutdown(socket.SHUT_WR)

	#recieve the response
	data = bytes([])
	while True:
		new_data = s.recv(1024)
		if not new_data: break
		data += new_data
	s.close()
	try:
		data = str(data,'UTF-8')
	except Exception as e:
		print("Bytes Return on Socket Request Malformed")
		return False,None
	
	#load the data using json load
	try:
		json_data = json.loads(data)
	except Exception as e:
		print("Json Return on Socket Request Malformed" + str(data))
		return False,None

	#build our queue_blogs json
	input_data = {"request_type":"new_blog_request",}	

	# get an available socket number
	try:
		if not json_data["worked"]:
			raise Exception("Socket Request Failed")
		queue_blogs_socket_number = (json_data["socket_number"])
	except Exception as e:
		print(e)
		return False,None

	#open that socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, queue_blogs_socket_number))
	except Exception as e:
		print("Payload Socket Didnt Open: " + str(e))
		return False,None

	#send it our payload
	try:
		send_data = json.dumps(input_data)
		s.send(str.encode(send_data))
		s.shutdown(socket.SHUT_WR)
	except Exception as e:
		print("Could Not Send Payload: " + str(e))
		return False,None

	#recieve the response
	data = bytes([])
	while True:
		new_data = s.recv(1024)
		if not new_data: break
		data += new_data
	s.close()
	try:
		data = str(data,'UTF-8')
	except Exception as e:
		print("Bytes Return on Socket Request Malformed")
		return False,None
	
	#load the data using json load
	try:
		json_data = json.loads(data)
	except Exception as e:
		print("Json Return on Socket Request Malformed" + str(data))
		return False,None

	#extract the new blog from the json
	try:
		if not json_data["worked"]:
			return False,None
		return True,json_data["new_blog"]
	except Exception as e:
		print("Json Return on New Blog Request Failed: " + str(e))
		return False, None

# get the blogs from notes
def get_blogs_from_notes(blog_name,api_key,offset=None,limit=None):

	#return list
	blogs = set([])

	# build url for api
	try:
		authentication = '?api_key=' + api_key
		url = 'http://api.tumblr.com/v2/blog/' + blog_name +".tumblr.com"
		parameters = "&notes_info=true&reblog_info=true"
		if limit != None:
			parameters += '&limit='+str(int(limit))
		if offset != None:
			parameters += '&offset='+str(int(offset))
		url += '/posts'+ authentication + parameters
	except Exception as e:
		print("Could not build")
		return False,[]

	# retrieve html
	try:
		response = urllib.request.urlopen(url)
		html = response.read()
	except Exception as e:
		print("Could not get Html",str(url))
		return False,[]

	# parse html into json
	try:
		x = json.loads(html.decode('UTF-8'))
	except Exception as e:
		print("Could not Parse to Json")
		return False,[]

	# look for "unique blogs"
	try:
		if "response" in x:
			if "posts" in x["response"]:
				for a in x["response"]["posts"]:
					if "notes" in a:
						for b in a["notes"]:
							if "blog_name" in b:
								if b["blog_name"] not in blogs:
									blogs.add(b["blog_name"])
	except Exception as e:
		print("Could Not Parse Json into Unique Blogs")
		return False,[]

	# return list of unique blogs in a list
	return True,list(blogs)

# sends the blogs to the frontier
def send_blogs_to_frontier(host,port,blogs):

	#connect to the frontier to get a socket to communicate with
	connection_success = False
	connection_success_fails = 0
	while not connection_success:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((host, port))
			connection_success = True
		except Exception as e:
			print("Could Not Link To Socket " + str(port))
			connection_success_fails += 1
			if connection_success_fails > 5:
				print("Max Link Fails to socket " + str(port))
				return False
			time.sleep(random.randrange(.1,.5))
			pass

	#send the json request for a socket
	s.send(str.encode(json.dumps({"request_type":"socket_request"})))
	s.shutdown(socket.SHUT_WR)

	#recieve the response
	data = bytes([])
	while True:
		new_data = s.recv(1024)
		if not new_data: break
		data += new_data
	s.close()
	try:
		data = str(data,'UTF-8')
	except Exception as e:
		print("Bytes Return on Socket Request Malformed")
		return False
	
	#load the data using json load
	try:
		json_data = json.loads(data)
	except Exception as e:
		print("Json Return on Socket Request Malformed" + str(data))
		return False

	#build our queue_blogs json
	input_data = 	{
						"request_type": "queue_blogs",
						"blog_list": blogs,
					}

	# get an available socket number
	try:
		if not json_data["worked"]:
			raise Exception("Socket Request Failed")
		queue_blogs_socket_number = (json_data["socket_number"])
	except Exception as e:
		print(e)
		return False

	#open that socket
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((host, queue_blogs_socket_number))
	except Exception as e:
		print("Payload Socket Didnt Open: " + str(e))
		return False

	#send it our payload
	try:
		send_data = json.dumps(input_data)
		s.send(str.encode(send_data))
		s.shutdown(socket.SHUT_WR)
		s.close()
	except Exception as e:
		print("Could Not Send Payload: " + str(e))
		return False
	return True

if __name__ == "__main__":
	try:

		blogs_visited = 0
		host = 'localhost'
		port = 8888

		#first send a starting blog to the frontier
		fail_count = 0
		while True:
			seed_blogs = ["just1boi"]
			ret = send_blogs_to_frontier(host,port,seed_blogs)
			if ret:
				break
			fail_count += 1
			if fail_count > 10:
				print("Failed on Send Blogs, Number of Blogs Visited: " + str(blogs_visited))
				sys.exit()
			time.sleep(.1)




		# main loop
		while True:

			#get a new blog from the frontier
			fail_count = 0
			new_blog = ''
			print("Get a New Blog From our Frontier")
			while True:
				ret,new_blog = get_blog_from_frontier(host,port)
				if ret:
					break
				fail_count += 1
				if fail_count > 10:
					print("Failed on Frontier New Blog Access, Number of Blogs Visited: " + str(blogs_visited))
					sys.exit()
				time.sleep(.1)

			#get the blogs from the notes of the new blog
			fail_count = 0
			insert_blogs = []
			print("Get Notes From Tumblr")
			while True:
				ret,insert_blogs = get_blogs_from_notes(new_blog,my_api_key)
				if ret:
					break
				fail_count += 1
				if fail_count > 10:
					print("Failed on tumblr access, Number of Blogs Visited: " + str(blogs_visited))
					sys.exit()
				time.sleep(1)

			#insert the blogs into our frontier
			fail_count = 0
			print("Insert New Blogs to our Frontier")
			while True:
				ret = send_blogs_to_frontier(host,port,insert_blogs)
				if ret:
					break
				fail_count += 1
				if fail_count > 10:
					print("Failed on Send Blogs, Number of Blogs Visited: " + str(blogs_visited))
					sys.exit()
				time.sleep(.1)

			blogs_visited += 1
			if blogs_visited %10 == 0:
				print("Visited " + str(blogs_visited) + " blogs successfully")

	finally:
		print("Ending: " + str(blogs_visited))
