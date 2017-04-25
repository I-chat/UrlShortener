[![Build Status](https://travis-ci.org/andela-iikikin/UrlShortener.svg?branch=bootstrap)](https://travis-ci.org/andela-iikikin/UrlShortener)
[![Coverage Status](https://coveralls.io/repos/github/andela-iikikin/UrlShortener/badge.svg?branch=bootstrap)](https://coveralls.io/github/andela-iikikin/UrlShortener?branch=bootstrap)
[![Dependency Status](https://gemnasium.com/badges/github.com/andela-iikikin/UrlShortener.svg)](https://gemnasium.com/github.com/andela-iikikin/UrlShortener)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/andela-iikikin/UrlShortener/badges/quality-score.png?b=bootstrap)](https://scrutinizer-ci.com/g/andela-iikikin/UrlShortener/?branch=bootstrap)
# PicoUrl
A URL shortening service application with a RESTful API which accepts request in `JSON` format and also sends responses in `JSON`.

## Dependencies
This application was built with:
* [Python 3](https://www.python.org/download/releases/3.0/) - Python is a programming language that lets you work quickly
and integrate systems more effectively.
* [Flask](http://flask.pocoo.org/) - Flask is a micro web framework written in Python and based on the [Werkzeug toolkit](http://werkzeug.pocoo.org/) and [Jinja2](http://jinja.pocoo.org/docs/2.9/) template engine.
* [SQLAlchemy](https://www.sqlalchemy.org/) as [ORM](https://en.wikipedia.org/wiki/Object-relational_mapping) and [SQLite](https://www.sqlite.org/index.html) for persisting data.
* [Flask-Bootstrap==3.3.7.1](https://pythonhosted.org/Flask-Bootstrap/) - Flask-Bootstrap packages Bootstrap into an extension that mostly consists of a blueprint named ‘bootstrap’. It can also create links to serve Bootstrap from a CDN.
* [Flask-HTTPAuth==3.2.2](https://flask-httpauth.readthedocs.io/en/latest/) - Flask-HTTPAuth is a simple extension that simplifies the use of HTTP authentication with Flask routes. Used for API authentication.
* [Flask-Login](https://flask-login.readthedocs.io/en/latest/) - Flask-Login provides user session management for Flask.
* [Flask-Migrate](https://flask-migrate.readthedocs.io/en/latest/) - Flask-Migrate is an extension that handles SQLAlchemy database migrations for Flask applications.
* [Flask-Script](https://flask-script.readthedocs.io/en/latest/) - Flask-Script extension provides support for writing external scripts in Flask.
* [Python-env](https://github.com/mattseymour/python-env/blob/master/README.md) - Get and Set environment variables using .env file
* [Validators](https://github.com/kvesteri/validators/blob/master/README.rst) - Python data validation.
* [voluptuous](https://github.com/alecthomas/voluptuous) - Python schema and data validation tool.

## Application Features
###### User Sign up and User Login
Users can sign up with an email address and password and also login with the same email address and password.
###### Shorten a URL
Users can send a long URL and get a shortened version of it.
A user can expect that following the shortened URL will lead to a redirection to the long URL.
###### Shorten a URL with vanity strings
Registered users can include a vanity string and expect a shortened URL composed of the vanity string.

###### View added URLs based on popularity and date added
Users can view shortened URL sorted by popularity and how recently they were added.

###### Delete, activate and deactivate a short URL
Registered users can delete, set short URLs to inactive and then set it back to active.
###### View details of visitors to a short URL
Registered users can access details such as ip address, system platform and user agent of visitors to a short URL.

## How to Install
### On a Unix based OS
* Install python 3 using `sudo apt-get install python3-dev`
* Install Virtualenvwrapper using `pip install Virtualenvwrapper`
* Make a new virtual environment using `mkvirtualenv --python=python3 <env_name>`
* Activate the new virtual environment using `workon <env_name>`
* Download and extract the project.
* cd into PicoUrl folder and run `pip install -r requirements.txt` from the terminal.
* Download and extract the project.
* cd into PicoUrl folder and run `pip install -r requirements.txt` from the command prompt.
* Create a .env file in the project root directory and set the following vairiable.
```
DEV_DATABASE_URL='file path to database to use during development.'
SECRET_KEY='random string used for encryption'
TEST_DATABASE_URL='file path to database to used for testing.'
SITE_URL='server in which app is being tested: `localhost:5000` works.'
```
* cd into the project root folder and run `python run.py runserver` to start the development server.

### On Windows OS
* Download and install the [python 3](https://www.python.org/downloads/windows/) package for Windows.
* Install Virtualenvwrapper-win using `pip3 install Virtualenvwrapper-win`
* On the command line run `where python3` and copy the path to the python3 interpreter.
* Make a new virtual environment using `mkvirtualenv --python=<path to the python3 interpreter> <env_name>`
* Activate the new virtual environment using `workon <env_name>`
* Download and extract the project.
* cd into PicoUrl folder and run `pip install -r requirements.txt` from the command prompt.
* Create a .env file in the project root directory and set the following vairiable.
```
DEV_DATABASE_URL='file path to database to use during development.'
SECRET_KEY='random string used for encryption'
TEST_DATABASE_URL='file path to database to used for testing.'
SITE_URL='server in which app is being tested: `localhost:5000` works.'
```
* cd into the project root folder and run `python run.py runserver` to start the development server.

## Testing
* cd into the project root directory
* run `python run.py test` or  `python run.py test --coverage` to run the test with coverage.


## API Documentation
-----
PicoUrl exposes its data via an Application Programming Interface (API), so developers can interact in a programmatic way with the application. This document is the official reference for that functionality.

### API Resource Endpoints

URL Prefix = `https://ich-at.herokuapp.com/api/v1` is the root URL of the server HOST.


| EndPoint                                 | Functionality                 | Public Access|
| -----------------------------------------|:-----------------------------:|-------------:|
| **GET** `/users/influential`            | Return a list of influential users and the number of URLs shortened.              |    FALSE     |
| **GET** `/shorturl/<int:id>/logs`        | Return the logs of visits to short URL  |    FALSE      |
| **GET** `/user/short_urls`           | Get all short_urls by a user  |    FALSE     |
| **GET** `/shorturl/<int:id>`         | Gets details of a short URL   |    FALSE     |
| **GET** `/user/         `            | Get details of the current user  | FALSE      |
| **GET** `/shorturl/popularity`       | Gets all short URL sorted by popularity      |    FALSE     |
| **GET** `/longurl/popularity`        | Gets all long URL sorted by popularity       |    FALSE     |
| **GET** `/shorturl/date`             | Get all shorturl sorted by how recently they were added |  FALSE   |
| **GET** `/token`                     | Request a token               |    FALSE     |
| **POST** `/register`                 | Register a user               |    TRUE     |
| **POST** `/shorten`                  | Shorten a long URL            |    FALSE     |
| **PUT** `/short_url/<int:id>/change_longurl` | Change the target URL of a short URL|   FALSE |
| **PUT** `/short_url/<int:id>/activate`      | Activate a short URL       |    FALSE     |
| **PUT** `/short_url/<int:id>/deactivate`    | Deactivate a short URL     |    FALSE     |
| **DELETE** `/short_url/<int:id>/delete` | Delete a short URL |    FALSE     |

#### Authentication
###### POST HTTP Request
-   `POST /register`
-   INPUT:
```json
{
	"firstname": "john",
	"lastname": "dilinger",
	"email": "john_dilinger@yahoo.com",
	"password": "1234567",
	"confirm_password": "1234567"
}
```
    ###### HTTP Response
-   HTTP Status: `201: created`
-   JSON data
```json
{
  "email": "john_dilinger@yahoo.com",
  "message": "Registration Successful."
}
```
###### POST HTTP Request
-   `GET /token`
-   Requires: User Authentication
    ###### HTTP Response
-   HTTP Status: `200: OK`
-   JSON data
```json
{
  "expiration": 3600,
  "token": "eyJhbGciOiJIUzI1NiIsImlhdCI6MTQ5MzA3NjkwMywiZXhwIjoxNDkzMDgwNTAzfQ.eyJpZCI6MX0.ZbVpMBSQWS0dHN1vtlUnjmra45pdRT9m1AkxMJit_38"
}
```
#### Shortening Service
###### POST HTTP Request
-   `POST /shorten`
-   INPUT:
```json
{
	"url": "http://www.google.com"
}
```
    ###### HTTP Response
-   HTTP Status: `201: created`
-   JSON data
```json
{
  "id": 1,
  "short_url": "http://localhost:5000/6eiJM2"
}
```
###### GET HTTP Request
-   `GET /users/influential`
-   Requires: User Authentication
    ###### HTTP Response
-   HTTP Status: `200: OK`
-   JSON data
```json
{
  "users_list": [
    {
      "Name": "koya gabriel",
      "No of URLs shortened": 4
    },
    {
      "Name": "ladi adeniran",
      "No of URLs shortened": 3
    },
    {
      "Name": "bolaji olajide",
      "No of URLs shortened": 1
    }
  ]
}
```
###### GET HTTP Request
-   `GET /shorturl/<int:id>/logs`
-   Requires: User Authentication
    ###### HTTP Response
-   HTTP Status: `200: OK`
-   JSON data
```json
{
  "short_url logs": [
    {
      "I.P Adress": "127.0.0.1",
      "System platform": "macos",
      "User agent": "chrome"
    },
    {
      "I.P Adress": "127.0.0.1",
      "System platform": null,
      "User agent": "PostmanRuntime/3.0.11-hotfix.2"
    },
    {
      "I.P Adress": "127.0.0.1",
      "System platform": "macos",
      "User agent": "chrome"
    },
    {
      "I.P Adress": "127.0.0.1",
      "System platform": "macos",
      "User agent": "safari"
    }
  ]
}
```
###### GET HTTP Request
-   `GET /user/short_urls`
-   Requires: User Authentication

    ###### HTTP Response
-   HTTP Status: `200: OK`
-   JSON data
```json
{
  "short_url list": [
    {
      "Active status": true,
      "Date_added": "Mon, 24 Apr 2017 20:20:09 GMT",
      "Times_visted": 4,
      "short_url": "http://localhost:5000/6eiJM2"
    },
    {
      "Active status": true,
      "Date_added": "Mon, 24 Apr 2017 23:52:32 GMT",
      "Times_visted": 0,
      "short_url": "http://localhost:5000/Gwu3rg"
    },
    {
      "Active status": true,
      "Date_added": "Mon, 24 Apr 2017 23:52:47 GMT",
      "Times_visted": 0,
      "short_url": "http://localhost:5000/wPh6L8"
    },
    {
      "Active status": true,
      "Date_added": "Mon, 24 Apr 2017 23:53:04 GMT",
      "Times_visted": 0,
      "short_url": "http://localhost:5000/70UEMg"
    }
  ]
}
```
###### GET HTTP Request
-   `GET /shorturl/<int:id>`
-   Requires: User Authentication
    ###### HTTP Response
-   HTTP Status: `200: OK`
-   JSON data
```json
{
  "Active status": true,
  "Date added": "Mon, 24 Apr 2017 20:20:09 GMT",
  "Times_visted": 4,
  "long_url": "http://www.google.com",
  "short_url": "http://localhost:5000/6eiJM2"
}
```
###### GET HTTP Request
-   `GET /user/`
-   Requires: User Authentication
    ###### HTTP Response
-   HTTP Status: `200: OK`
-   JSON data
```json
{
  "email": "portable@yahoo.com",
  "firstname": "idetu",
  "lastname": "ikikin",
  "no of URL shortened": 4
}
```
###### GET HTTP Request
-   `GET /shorturl/popularity`
-   Requires: User Authentication
    ###### HTTP Response
-   HTTP Status: `200: OK`
-   JSON data
```json
{
  "url_list": [
    {
      "Times_visted": 4,
      "date_added": "Mon, 24 Apr 2017 20:20:09 GMT",
      "short_url": "6eiJM2"
    },
    {
      "Times_visted": 0,
      "date_added": "Mon, 24 Apr 2017 23:52:32 GMT",
      "short_url": "Gwu3rg"
    },
    {
      "Times_visted": 0,
      "date_added": "Mon, 24 Apr 2017 23:52:47 GMT",
      "short_url": "wPh6L8"
    },
    {
      "Times_visted": 0,
      "date_added": "Mon, 24 Apr 2017 23:53:04 GMT",
      "short_url": "70UEMg"
    }
  ]
}
```
## Authors

**Ikikin Ichiato O.** - Software Developer at Andela

## Acknowledgments

Thanks to my facilitator **Njira Perci** and my wonderful **Pygo Teammates**
