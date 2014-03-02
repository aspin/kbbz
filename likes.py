import facebook
import time

## Written for Python 2.7.3 ##

## TO DO LIST:
## 		1. Add other needed attributes.
##		2. Add in function to collect all data from friends and
##		   aggregate all status data.

token = ""
graph = 0

def setToken(t):
	global token, graph
	token = t
	graph = facebook.GraphAPI(token)

#### Data collection ####

## Statuses ##

def getUserData(limit, uid="me", l2=1000):
	statuses = getStatuses(uid, limit, l2)
	
	stat_data = []
	for i in range(len(statuses)):
		stat_data.append([getMessage(statuses[i]), countLikes(statuses[i]), statuses[i]['updated_time']])

	return stat_data

def getStatuses(uid, l, l2=1000):
	return graph.get_connections(uid, "statuses", limit=l, fields="likes.limit("+str(l2)+"),message")['data']

def countLikes(status):
	if 'likes' in status:
		return len(status['likes']['data'])
	return 0

def getMessage(status):
	if 'message' in status:
		return status['message']
	return ""

# Super expensive operations #
def getAllFriendsStatuses(limit):
	friends = graph.get_connections("me", "friends")['data']

	friend_statuses = []
	for i in friends:
		uid = str(i['id'])
		friend_statuses.append(getUserData(limit, uid))

	return friend_statuses

def getAverageFriendLikes(limit):
	friends = graph.get_connections("me", "friends")['data']

	total_likes = 0
	total_statuses = 0

	for i in friends:
		statuses = getUserData(limit, str(i['id']))
		total_statuses += len(statuses)
		total_likes += total_statuses * getAverageLikes(statuses)

	return total_likes / total_statuses

## User Attributes ##

#age, gender, location, number of friends
def getUserInfo(uid):
	profile = graph.get_object(uid)
	gender = getGender(profile)
	age = getAge(profile)
	location = getLocation(uid)
	numFriends = countFriends(uid)

	return [age, gender, location, numFriends]

def getGender(profile):
	if 'gender' in profile:
		return profile['gender']
	return "?"

#information rarely available
def getAge(profile):
	try:
		birthday = profile['birthday']
		year = time.strftime("%Y")
		return eval(year) - eval(birthday[6:])
	except:
		return "?"

def getLocation(uid):
	loc = graph.get_connections(uid, "", fields="location")
	if 'location' in loc:
		return loc['location']['name'] # not sure what formwat we want here

def countFriends(uid):
	if uid == "me":
		uid = "me()"
	count = graph.fql("SELECT friend_count FROM user WHERE uid=" + uid)['data'][0]
	if 'friend_count' in count:
		return count['friend_count']
	return "?"

#### Data Output ####

# individual friend files
def printFriendFiles(limit, total, directory=""):
	friends = graph.get_connections("me", "friends")['data']

	number = 1

	for i in friends:

		friend_id = str(i['id'])
		friend_statuses = getUserData(limit, friend_id)

		try:
			d = (directory + str(i['name'])).lower().replace(" ", "_")
			fileOut = open(d, 'w')
		except:
			fileOut = open(directory + "profile_" + str(number), 'w')
		for i in friend_statuses:
			print >>fileOut, i
		fileOut.close()
		number += 1

		if number == total:
			return "Completed."
	return "Completed."

# aggregate dataset of all friends


#### Data analysis / Utility ####

def getLikesAbove(data, n):

	lst = []
	for i in data:
		if i[1] >= n:
			lst.append(i)
	return lst

def getAverageLikes(data):
	total = 0
	numStatuses = 0
	for i in data:
		total += i[1]
		numStatuses += 1
	return round(float(total) / numStatuses, 3)

def getFriendID(name):
	nameIn = name.split(" ")
	friends = graph.get_connections("me", "friends")['data']
	matches = []

	for i in friends:
		try:
			names = str(i['name']).lower().split(" ")
			for j in nameIn:
				if j.lower() in names:
					matches.append(i)
		except:
			print "Name not processsed: " + i['name']

	return matches

