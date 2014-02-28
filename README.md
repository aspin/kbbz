==========
kbbz
==========

Setup:

::
	import likes
::
	likes.setToken(access_token)

My statuses:

::
	statuses = likes.getMyData(num_statuses)
	
Friend's statuses:

::
	statuses = likes.getMyData(num_statuses, friend_id)
	
	
Printing to data files:

::
	likes.printFriendFiles(num_statuses, num_friends, directory)  ## end directory with a /
	

Bugs/Notes
==========

1. In-built Facebook API limitation to 100 statuses?
2. Relies on users providing tokens. Develop a better interface.
3. Names with special characters will not be printed properly. Instead, Profile XX will be
   printed with XX being the number of the profile being processed.
