kbbz
==========

Usage
----------

Run from terminal:

	python -i likes.py

You will then be prompted for an access token, which can be generated at https://developers.facebook.com/tools/explorer/

*	Under User Data Permissions, check `user_about_me`, `user_birthday`, `user_friends`, `user_hometown`, `user_location`, `user_status`
*	Under Friends Data Permissions, check `friends_about_me`, `friends_birthday`, `friends_hometown`, `friends_location`, `friends_status` and `friends_activities`

Wait for the program to finish running. Data files will be outputted to a data folder. This will take around 10-20 mins for a Facebook user with around 600 friends and a reasonably modern computer.

