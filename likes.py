from __future__ import print_function
import facebook
import time
from nltk.corpus import stopwords
import math

## Written for Python 2.7.3 ##

## TO DO LIST:
## 		1. Add other needed attributes.
##		2. Add in function to collect all data from friends and
##		   aggregate all status data.

token = ""
graph = 0
scorer = {}
attributes = """
@attribute 'age' numeric
@attribute 'gender' {male,female}
@attribute 'friend_count' numeric
@attribute 'message_score' numeric
@attribute 'month' numeric
@attribute 'hour' numeric
@attribute 'time_since_last' numeric
@attribute 'likes' numeric 

@data"""

def setToken(t):
	global token, graph
	token = t
	graph = facebook.GraphAPI(token)

def initDict():
	global scorer
	statuses = getOnlyStatusesLikes(100, "me")
	statuses += getAllFriendsOnlyStatusesLikes(100)
	
	scorer = buildWordDict(statuses)

#### Data collection ####

def getAllUserData(limit, uid="me", l2=1000):
	user_statuses = getUserStatuses(limit, uid, l2)
	user_info = getUserInfo(uid)

	for i in range(len(user_statuses)):
		user_statuses[i] = user_info + user_statuses[i]
	return user_statuses

## Statuses ##

def getUserStatuses(limit, uid, l2, mode="score"):
	statuses = getStatuses(uid, limit, l2)
	
	stat_data = []
	# retains status messages
	if mode == "message":
		for i in range(len(statuses)):
		 	stat_data.append([getMessage(statuses[i]), int(statuses[i]['updated_time'][5:7]), \
		 		int(statuses[i]['updated_time'][11:13]), countLikes(statuses[i])])

	# outputs score
	if mode == "score":
		for i in range(len(statuses)):
			stat_data.append([calcStatusScore(getMessage(statuses[i]), scorer), \
			int(statuses[i]['updated_time'][5:7]), int(statuses[i]['updated_time'][11:13]), countLikes(statuses[i])])

	for i in range(len(stat_data)-1):
		stat_data[i].insert(3, getTimeDifference(statuses[i]['updated_time'], statuses[i+1]['updated_time']))

	if stat_data:
		stat_data[len(stat_data)-1].insert(3, "?")

	return stat_data

#status + likes only
def getOnlyStatusesLikes(limit, uid, l2=1000):
	statuses = getStatuses(uid, limit, l2)
	
	stat_data = []
	for i in range(len(statuses)):
		stat_data.append([getMessage(statuses[i]), countLikes(statuses[i])])

	return stat_data

#helper status data gathering functions
def getStatuses(uid, l, l2=1000):
	return graph.get_connections(uid, "statuses", limit=l, fields="likes.limit("+str(l2)+"),message")['data']

def countLikes(status):
	if 'likes' in status:
		numLikes = len(status['likes']['data'])
		if numLikes == 0:
			return 0
		else:
			return math.log(len(status['likes']['data']))
	return 0

def getMessage(status):
	if 'message' in status:
		return status['message']
	return ""

def getTimeDifference(time1, time2):
	total1 = 0  #in seconds
	total2 = 0

	total1 += int(time1[0:4]) * 365 * 24 * 60 * 60
	total1 += int(time1[5:7]) * 30 * 24 * 60 * 60
	total1 += int(time1[8:10]) * 24 * 60 * 60
	total1 += int(time1[11:13]) * 60 * 60
	total1 += int(time1[14:16]) * 60
	total1 += int(time1[17:19])

	total2 += int(time2[0:4]) * 365 * 24 * 60 * 60
	total2 += int(time2[5:7]) * 30 * 24 * 60 * 60
	total2 += int(time2[8:10]) * 24 * 60 * 60
	total2 += int(time2[11:13]) * 60 * 60
	total2 += int(time2[14:16]) * 60
	total2 += int(time2[17:19])

	return total1 - total2

# Super expensive operations #
def getAllFriendsStatuses(limit):
	friends = graph.get_connections("me", "friends")['data']

	friend_statuses = []
	for i in friends:
		uid = str(i['id'])
		friend_statuses.append(getUserStatuses(limit, uid))

	return friend_statuses

def getAllFriendsOnlyStatusesLikes(limit):
	friends = graph.get_connections("me", "friends")['data']

	friend_statuses = []
	for i in friends:
		uid = str(i['id'])
		data = getOnlyStatusesLikes(limit, uid)
		print(i['name'] + ", " + str(len(data)))
		for j in data:
			friend_statuses.append(j)

	return friend_statuses
## User Attributes ##

#age, gender, location, number of friends
def getUserInfo(uid):
	profile = graph.get_object(uid)
	gender = str(getGender(profile))
	try:
		age = int(getAge(profile))
	except:
		age = str(getAge(profile))
	#location = getLocation(uid)
	numFriends = countFriends(uid)

	return [age, gender, numFriends]

#helper user info functions
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
		location = loc['location']['name']
		state = location.split(" ")[1]
		return state # not sure what format we want here
	return "?"

def countFriends(uid):
	if uid == "me":
		uid = "me()"
	count = graph.fql("SELECT friend_count FROM user WHERE uid=" + uid)['data'][0]
	if 'friend_count' in count:
		return count['friend_count']
	return "?"

## Message Score Calclation ##

def buildWordDict(statusArray):
	wordDict = dict()
	sw = set(stopwords.words('english'))
	for i in statusArray:
		if i == []:
			continue
		s = i[0]
		l = i[1]
		s = filter(lambda w: not w.lower() in sw, s.split())
		likes = l * 1.0
		if len(s) == 0:
			wscore = 0;
		else:
			wscore = likes / len(s)

		for w in s:
			if w not in wordDict:
				wordDict[w] = (1,wscore)
			else:
				count, sumScore = wordDict[w]
				wordDict[w] = (count+1, sumScore+wscore)

	return wordDict

def calcStatusScore(status,wordDict):
	score=0
	count=0
	for w in status.split(" "):
		if w in wordDict:
			wscore = wordDict[w][1] / wordDict[w][0]
			score+=wscore
			count+=1
	if count == 0:
		return 0
	return score/count

#### Data Output ####

# aggregate dataset of all friends
def printAllStatuses(limit, total):
	friends = graph.get_connections("me", "friends")['data']

	n = 1
	training = open("data/training.csv", 'w')
	print("@relation training", file=training)
	print(attributes, file=training)

	validation = open("data/validation.csv", 'w')
	print("@relation validation", file=validation)
	print(attributes, file=validation)

	test = open("data/test.csv", 'w')
	print("@relation test", file=test)
	print(attributes, file=test)

	my_data = getAllUserData(limit)
	for i in range(0, len(my_data), 3):
		printLine(training, my_data[i])
		if i+1 < len(my_data):
			printLine(validation, my_data[i+1])
		if i+2 < len(my_data):
			printLine(test, my_data[i+2])

	for i in friends:
		friend_id = str(i['id'])
		friend_data = getAllUserData(limit, friend_id)

		for i in range(0, len(friend_data), 3):
			printLine(training, friend_data[i])
			if i+1 < len(friend_data):
				printLine(validation, friend_data[i+1])
			if i+2 < len(friend_data):
				printLine(test, friend_data[i+2])

		n += 1

		if n == total:
			training.close()
			validation.close()
			test.close()
			return "Completed."

	training.close()
	validation.close()
	test.close()
	return "Completed."

def printLine(fn, lst):
	for i in lst:
		try:
			print(i, file=fn, end=",")
		except:
			print("?", file=fn, end=",")
	print("", file=fn)
	return

def printOnlyStatusesLikes(limit, total):
	friends = graph.get_connections("me", "friends")['data']
	fn = open("data/statuses-likes.txt", 'w')

	number = 1

	my_data = getOnlyStatusesLikes(limit, "me")
	for i in my_data:
		print(i, file=fn)

	for i in friends:

		friend_id = str(i['id'])
		friend_statuses = getOnlyStatusesLikes(limit, friend_id)

		for i in friend_statuses:
			print(i, file=fn)

		number += 1

		if number == total:
			fn.close()
			return "Completed."
	fn.close()
	return "Completed."

#### Post-Processing ####
def removeEndCommas(fileIn, fileOut):
	fIn = open(fileIn, 'r')
	fOut = open(fileOut, 'w')

	for line in fIn:

		length = len(line)

		if ",\n" in line:
			print(line[:length-2], file=fOut)
		else:
			print(line, end="", file=fOut)

	fIn.close()
	fOut.close()

	return "Completed."

def addQuestionMarks(fileIn, fileOut):
	fIn = open(fileIn, 'r')
	fOut = open(fileOut, 'w')

	for line in fIn:

		if line[0] == "@" or line[0] == "\n":
			print(line, end="", file=fOut)
		else:
			length = len(line)-1
			while line[length] != ",":
				length -= 1
			print(line[:length+1]+"?", file=fOut)

	fIn.close()
	fOut.close()

	return "Completed."

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
			print("Name not processsed: " + i['name'])

	return matches


## DEPRECATED FUNCTIONS THAT ARE NOT YET DELETED ##

# # individual friend files
# def printFriendFiles(limit, total, directory=""):
# 	friends = graph.get_connections("me", "friends")['data']

# 	number = 1

# 	for i in friends:

# 		friend_id = str(i['id'])
# 		friend_statuses = getUserStatuses(limit, friend_id)

# 		try:
# 			d = (directory + str(i['name'])).lower().replace(" ", "_")
# 			fileOut = open(d, 'w')
# 		except:
# 			fileOut = open(directory + "profile_" + str(number), 'w')
# 		for i in friend_statuses:
# 			print(i, file=fileOut)
# 		fileOut.close()
# 		number += 1

# 		if number == total:
# 			return "Completed."
# 	return "Completed."

# def getAverageFriendLikes(limit):
# 	friends = graph.get_connections("me", "friends")['data']

# 	total_likes = 0
# 	total_statuses = 0

# 	for i in friends:
# 		statuses = getUserStatuses(limit, str(i['id']))
# 		total_statuses += len(statuses)
# 		total_likes += total_statuses * getAverageLikes(statuses)

# 	return total_likes / total_statuses
