# Instructions for setting up the app #


### Requirements: 
[Python 2.7.9 or above (from Python 2 versions)](https://www.python.org/downloads) 

Includes pip package manager(Note: you can also use previous python versions, but you must ensure that you also have pip package manager installed. 2.7.9 and above comes with pip included)

* Clone the existing project

* Navigate inside the cloned folder and run
`pip install -r requirements.txt`
(Note: For linux users: if you get access problems, try to run it as superuser. For windows users: You may need to add the path containing pip in your installation to your environment PATH variable. Any user: You can also use virtualenv, but is not necessary)

* After installing the dependencies, run the following sequence of commands:

`python manage.py migrate`

`python manage.py runserver`

You must now have the app up and running

In case you want to clear the cache/database, navigate to the base folder and run the command 
`python manage.py flush`
