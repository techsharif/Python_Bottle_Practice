"""
Created on Mar 3, 2014

@author: steve
"""

import unittest
from webtest import TestApp
import sqlite3
import bottle
from bottle.ext import sqlite
from database import create_tables, sample_data
import main

DATABASE_NAME = "test.db"
# initialise the sqlite plugin for bottle
main.app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
bottle.debug()


class Level1FunctionalTests(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(main.app)
        # init an in-memory database
        db = sqlite3.connect(DATABASE_NAME)
        create_tables(db)
        self.users, self.positions = sample_data(db)

    def tearDown(self):
        pass

    def testHomepage(self):
        """As a visitor to the site, when I load the
         home page I see a banner with "Welcome to Jobs"."""

        result = self.app.get('/')
        result.mustcontain("Welcome to Jobs")

    def testAboutSiteLink(self):
        """As a visitor to the site, when I load the home page I see a link to another page
called "About this site".
"""
        result = self.app.get('/')
        links = result.html.find_all('a')

        self.assertTrue(any(['About' in l.text for l in links]), "Can't find 'About this site' link")

    def testAboutSitePage(self):
        """As a visitor to the site, when I click on the link "About" I am taken to
a page that contains the site manifesto, including the words "Jobs is a new, exciting,
job posting service like nothing you've seen before!"
        """

        message = "Jobs is a new, exciting, job posting service like nothing you've seen before!"

        result = self.app.get('/')

        newresult = result.click(description="About")

        # now look for our message in the page
        newresult.mustcontain(message)

    def testPageCSS(self):
        """As a visitor to the site, I notice that all the pages on the site have the same
design with the same colours and fonts used throughout.
        Interpret this as having a CSS file linked in the pages"""

        result = self.app.get('/')
        links = result.html.find_all('link', rel='stylesheet')

        self.assertGreater(len(links), 0, "No CSS stylesheet linked to home page")


if __name__ == "__main__":
    unittest.main()