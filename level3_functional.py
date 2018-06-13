"""
@author: Steve Cassidy
"""
import unittest
import sqlite3
from bottle.ext import sqlite
import bottle
from webtest import TestApp
from random import choice
import os

from database import create_tables, sample_data
import main
import users

DATABASE_NAME = "test.db"
# initialise the sqlite plugin for bottle
main.app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
bottle.debug()


class Level3FunctionalTests(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(main.app)
        self.db = sqlite3.connect(DATABASE_NAME)
        create_tables(self.db)
        self.users, self.positions = sample_data(self.db)

    def tearDown(self):
        self.db.close()
        os.unlink(DATABASE_NAME)

    def doLogin(self, user, password):
        """Perform a login with some validation along the way"""
        
        response = self.app.get('/')

        loginform = response.forms['loginform']

        self.assertIsNotNone(loginform, "no form with id loginform in the page")

        # login form action should be /login
        self.assertEqual('/login', loginform.action, "login form action should be '/login'")
 
        # the form has a user field
        self.assertIn('nick', loginform.fields)
        
        # and a password field
        self.assertIn('password', loginform.fields)

        loginform['nick'] = user
        loginform['password'] = password

        response = loginform.submit()

        return response

    def testLoginForms(self):
        """As a visitor to the site, when I load the home page, 
        I see a form with entry boxes for email and password and a button labelled Login."""

        (password, nick, avatar) = self.users[0]
                
        # As a registered user, when I enter my username (Bobalooba) and password
        # (bob) into the login form and click on the Login button,
        
        response = self.doLogin(nick, password)

        if response.status not in ['302 Found', '303 See Other']:
            self.fail("Expected a redirect response (302/303) after login")

        if response.headers['Location'] not in ['/', 'http://localhost:80/']:
            self.fail("Expected redirect location to be the root path '/'")

        # The response also includes a cookie with the name 
        # sessionid that contains some kind of random string.

        self.assertIn(users.COOKIE_NAME, self.app.cookies)
        sessionid = self.app.cookies[users.COOKIE_NAME]
        # let's just check that it's not the username
        self.assertNotEqual(nick, sessionid)

    def testLoginError(self):
        """As a registered user, when I enter my email address but get my 
        password wrong and click on the Login button, the page I get in 
        response contains a message "Login Failed, please try again". 
        The page also includes another login form."""
         
        (password, nick, avatar) = self.users[0]

        # try an invalid password
        response = self.doLogin(nick, 'not the password')

        # should see a page returned with the word Failed somewhere
        self.assertEqual('200 OK', response.status)
        self.assertIn("Failed", response)

        # Should not have a cookie
        self.assertNotIn(users.COOKIE_NAME, self.app.cookies)

        # and a login form
        self.assertIn('loginform', response.forms)

    def testLoginPagesLogoutForm(self):
        """As a registered user, once I have logged in,
         every page that I request contains my name and the logout form."""

        (password, nick, avatar) = self.users[0]

        response1 = self.doLogin(nick, password)
        response2 = self.app.get('/')

        # no login form
        self.assertNotIn('loginform', response2.forms)

        # but a logout form
        self.assertIn('logoutform', response2.forms)
        logoutform = response2.forms['logoutform']
        self.assertEqual('/logout', logoutform.action)

        # and the message "Logged in as XXX"
        self.assertIn("Logged in as %s" % nick, response2)

    def testLogoutForm(self):
        """As a registered user, once I have logged in, if I click on the Logout
        button in a page, the page that I get in response is the site home
        page which now doesn't have my name and again shows the login form."""

        (password, nick, avatar) = self.users[0]

        response1 = self.doLogin(nick, password)
        response2 = self.app.get('/')

        # and a logout form
        self.assertIn('logoutform', response2.forms)
        logoutform = response2.forms['logoutform']

        response3 = logoutform.submit()
        # response should be a redirect
        if response3.status not in ['302 Found', '303 See Other']:
            self.fail("Expected a redirect response (302/303) after login")

        if response3.headers['Location'] not in ['/', 'http://localhost:80/']:
            self.fail("Expected redirect location to be the root path '/'")

        response4 = self.app.get('/')
        # should see login form again
        loginform = response4.forms['loginform']
        self.assertIsNotNone(loginform, "no form with id loginform in the page")

    def testCreatePosition(self):
        """As a registered user, I can fill out a form on the main
        page to create a new position, when I submit the form I am redirected
        to the main page and my new position appears in the list"""

        (password, nick, avatar) = self.users[0]

        # generate a random string to look for in the post, use it in a URL that should be
        # turned into a link
        letters = "abcdefghijklmnopqrstuvwxyz1234560928"
        randomstring = ''.join([choice(letters) for i in range(20)])

        testmessage = "<p>Job description with <b>Markup!</b> &lt; foo</p>"

        response = self.doLogin(nick, password)
        response = self.app.get('/')

        self.assertIn('postform', response)

        form = response.forms['postform']
        self.assertEqual('/post', form.action, "post form action should be '/post'")

        form['title'] = randomstring
        form['company'] = "Acme Inc"
        form['location'] = 'Sydney'
        form['description'] = testmessage

        response = form.submit()

        # check response

        self.assertEqual('302 Found', response.status)
        self.assertEqual('http://localhost:80/', response.headers['Location'])

        # fetch home page and look for our random string to check that the post is there

        response = self.app.get('/')
        self.assertIn(randomstring, response)


if __name__ == "__main__":
    unittest.main(warnings='ignore')
