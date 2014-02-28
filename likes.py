import facebook

## Written for Python 2.7.3 ##

## Data collection ##

token = ""

def setToken(t):
	global token
	token = t

def getStatuses(id, l, l2=1000):
	return facebook.GraphAPI(token).get_connections(id, "statuses", limit=l, fields="likes.limit("+str(l2)+"),message")['data']

def countLikes(status):
	if 'likes' in status:
		return len(status['likes']['data'])
	return 0

def getMessage(status):
	if 'message' in status:
		return status['message']
	return ""

def getMyData(limit, id="me", l2=1000):
	statuses = getStatuses(id, limit, l2)
	
	stat_data = []
	for i in range(len(statuses)):
		stat_data.append([getMessage(statuses[i]), countLikes(statuses[i]), statuses[i]['updated_time']])

	return stat_data

def getFriendID(name):
	friends = facebook.GraphAPI(token).get_connections("me", "friends")['data']
	matches = []

	for i in friends:
		try:
			names = str(i['name']).split(" ")
			if name in names:
				matches.append(i)
		except:
			print "Name not processsed, added automatically."
			matches.append(i)

	return matches

def getFriendsStatuses(limit):
	friends = facebook.GraphAPI(token).get_connections("me", "friends")['data']

	friend_statuses = []
	for i in friends:
		friend_id = str(i['id'])
		friend_statuses.append(getMyData(limit, friend_id))

	return friend_statuses


## Data analysis ##

def getLikesAbove(data, n):

	lst = []
	for i in data:
		if i[1] >= n:
			lst.append(i)
	return lst

## Data storage ##

def printFriendFiles(limit, total, directory=""):
	friends = facebook.GraphAPI(token).get_connections("me", "friends")['data']

	number = 1

	for i in friends:

		friend_id = str(i['id'])
		friend_statuses = getMyData(limit, friend_id)

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
