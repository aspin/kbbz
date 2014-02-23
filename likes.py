import facebook

## Written for Python 2.7.3 ##

##                  BUGS/NOTES                      ##
#  1. In-built limitation to 100 statuses?  
#  2. Currently relies on users providing tokens
#  3. 

## Data collection ##

token = "CAACEdEose0cBAAtxMXNDRb6LMnYuLDcoQ59wVhSung2i0CCiKOIBrURZBm3ZAoGdzWTFBf0kHUALbOQ8ViZB2yPstoJRWuPdk2WPDzDSGDVjZA4x8jengr3L1RFqW68oDMaesyPdyDViYbnrwSoGFUJ8Gz5kBZC4tXuev3GRyKFYABr7lkwKnYfYPigHLozZADcIrbZCZCjVYwZDZD"

def setToken(t):
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
