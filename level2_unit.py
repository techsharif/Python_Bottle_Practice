"""
@author: Steve Cassidy

"""
import unittest
import sqlite3

from database import create_tables, sample_data
import interface


class LevelAUnitTests(unittest.TestCase):

    def setUp(self):
        # open an in-memory database for testing
        self.db = sqlite3.connect(":memory:")
        create_tables(self.db)
        self.users, self.positions = sample_data(self.db)

    def test_position_list(self):
        """Test that position_list returns positions"""

        # first get all positions
        positions = interface.position_list(self.db, limit=1000)

        self.assertEqual(len(self.positions), len(positions))

        # validate the returned values

        self.assertEqual(1, positions[0][0])
        self.assertEqual('2018-03-07 22:36:19', positions[0][1])
        # can't check owner as it is randomly assigned
        self.assertEqual('Staff Site Reliability Engineer ', positions[0][3])

    def test_position_list_limit(self):
        """Test that position_list returns positions using the limit argument"""

        # now look at the limit argument
        positions = interface.position_list(self.db, limit=3)
        self.assertEqual(3, len(positions))

        positions = interface.position_list(self.db, limit=1)
        self.assertEqual(1, len(positions))

        # limit higher than number of positions
        positions = interface.position_list(self.db, limit=100)
        self.assertEqual(50, len(positions))

    def test_position_get(self):
        """Test getting position details from the id"""

        position = interface.position_get(self.db, 1)

        self.assertEqual("CircleCI", position[5])
        self.assertEqual("Staff Site Reliability Engineer ", position[3])

        # get a position that doesn't exist, result should be None
        position = interface.position_get(self.db, 9999999)
        self.assertIsNone(position)

    def test_position_add(self):
        """Test adding new positions"""

        usernick = 'Bean'
        title = "Sample Job Ad"
        location = "Sydney"
        company = "ACME Widgets"
        description = "This is the description"

        # get an initial count of positions
        positioncount = len(interface.position_list(self.db, limit=1000))

        result = interface.position_add(self.db, usernick, title, location, company, description)

        # should have returned True for succesful insertion
        self.assertTrue(result)

        # should now have one more position
        positions = interface.position_list(self.db, limit=1000)
        self.assertEqual(1, len(positions)-positioncount)

        # check the latest one is the one we added
        self.assertEqual(title, positions[0][3])

    def test_position_add_bad_usernick(self):
        """Test adding new positions"""

        usernick = 'Nonexistant'
        title = "Sample Job Ad"
        location = "Sydney"
        company = "ACME Widgets"
        description = "This is the description"

        # get an initial count of positions
        positioncount = len(interface.position_list(self.db, limit=1000))

        result = interface.position_add(self.db, usernick, title, location, company, description)

        # should have returned False because the user nick does not exist
        self.assertFalse(result)

        # should have the same number of positions
        positions = interface.position_list(self.db, limit=1000)
        self.assertEqual(positioncount, len(positions))




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()