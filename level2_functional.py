"""
@author: Steve Cassidy
"""

import unittest
import sqlite3
import os
from bottle.ext import sqlite
import bottle
import html
from webtest import TestApp
from database import create_tables, sample_data
import main, interface

DATABASE_NAME = "test.db"
# initialise the sqlite plugin for bottle
main.app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
bottle.debug()


class Level2FunctionalTests(unittest.TestCase):

    def setUp(self):
        self.app = TestApp(main.app)
        self.db = sqlite3.connect(DATABASE_NAME)
        create_tables(self.db)
        self.users, self.positions = sample_data(self.db)

    def tearDown(self):
        self.db.close()
        os.unlink(DATABASE_NAME)

    def test_home_page_lists_posts(self):
        """As a visitor to the site, when I load the home page I see a list of
        up to 10 positions in order of time, most recent first
        """
        
        result = self.app.get('/')
        # look for the title of each position in the returned page
        # need to escape any special characters
        # need the most recent 10 posts which are the first ones in self.positions
        for position in self.positions[:10]:
            title = html.escape(position[2])
            self.assertIn(title, result)

        # check the order of positions, look for the date strings
        # and check that they occur in order
        lastloc = -1
        dates = [position[0] for position in self.positions[:10]]
        for date in sorted(dates, reverse=True):
            loc = result.text.find(date.strftime("%Y-%m-%d %H:%M:%S"))
            self.assertNotEqual(-1, loc, "date string '%s' not found in page" % date)
            self.assertGreaterEqual(loc, lastloc, "date string '%s' occurs out of order" % date)
            lastloc = loc

    def test_position_page(self):
        """As a visitor to the site, I can click on the "Read More" link
        after a position description on the home page,
        I see a page with the full description of the position at
        the URL /positions/DD where DD is the position id."""

        response = self.app.get('/')

        # find a Read More link
        links = response.html.findAll('a', text="Read More")
        self.assertNotEqual(0, len(links), "Could not find any 'Read More' links in home page.  Link must have this exact text.")
        url = links[0]['href']
        self.assertTrue(url.startswith("/positions/"), "'Read More' URL should start with /positions/")
        response = self.app.get(url)
        self.assertEqual('200 OK', response.status)

    def test_position_page_content(self):
        """Test that the page at /positions/DD has the description
        of the position number DD"""

        # test relies on interface.position_get working

        id = 10
        position = interface.position_get(self.db, id)
        self.assertEqual(7, len(position))
        self.assertEqual(id, position[0])

        # now get the page
        response = self.app.get('/positions/%d' % id)
        # and look for the details
        for data in position[1:5]:
            escaped = html.escape(data)
            self.assertIn(escaped, response)
        # but the description should not be escaped
        self.assertIn(position[6], response)

if __name__ == "__main__":
    unittest.main()