
kbbz
==========

Setup
----------

Run from terminal:

	python -i likes.py

Generate some sort of OAuth Token

	setToken(access_token)

Usage
----------

My statuses:

	statuses = getMyData(num_statuses)
	
Friend's statuses:

	statuses = getMyData(num_statuses, friend_id)
	
	
Printing to data files:

	printFriendFiles(num_statuses, num_friends, directory)  ## end directory with a /
	
Look up Friend ID:

	getFriendID(name) ## automatically considers all names with special characters

Get user attributes (unknown attributes represented with a "?"):

	getUserInfo(user_id)


Bugs/Notes/To-do/etc.
----------

1. In-built Facebook API limitation to 100 statuses?
2. Relies on users providing tokens. Develop a better interface.
3. Names with special characters will not be printed properly. Instead, Profile XX will be
   printed with XX being the number of the profile being processed.
4. We can't seem to pull friends of friends and so we can't get statistics on their numbers of likes.
   The functions that this most impacts is counting the average number of likes among friends
   (which is super expensive already), because that would require us to pull all Facebook statuses of
   friends of friends (both prohibitive by both computation time and what data we can access)