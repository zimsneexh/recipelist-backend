# Recipelist Backend written in Python3

Recipelist backend parsing data from OpenDataHub's tourism data set. 
Supports storing ratings in a SQLite database and user authentication.

## Setup guide
Install all listed [dependencies](#dependencies) using setup.py and pip

### Install branchweb

- python3 setup.py sdist
- python3 -m pip install dist/branchweb...

### Install branchlog

- python3 setup.py sdist
- python3 -m pip install dist/branchlog...

## Endpoints

### GET: /recipelist
A list of recipes

### GET: /?getimage=[UID]
Gets a specific image

### GET: /?getdetail=[UID]
Gets recipe details

### POST: /auth
Used to authenticate a user using user and password

###  POST: /checkauth
Check if an authentication key is still valid

### POST: /logoff
Invalidate a provided authkey

### POST: /createuser
Create a new user from provided user and password

### POST: /addrating
Adds a rating to a given recipe

## Dependencies
The API uses the [branchweb](https://github.com/AcaciaLinux/branchweb) and [branchlog](https://github.com/AcaciaLinux/branchlog) modules  from [branch](https://github.com/AcaciaLinux/branch).