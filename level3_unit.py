"""
@author: Steve Cassidy
"""

import unittest
import sqlite3

from database import create_tables, sample_data
from http.cookies import SimpleCookie

# import the modules to be tested
import users
from bottle import request, response


class Test(unittest.TestCase):

    def setUp(self):
        # open an in-memory database for testing
        self.db = sqlite3.connect(":memory:")
        create_tables(self.db)
        self.users, self.positions = sample_data(self.db)

    def test_check_login(self):
        """Test check_login for good and bad passwords"""

        for password, nick, avatar in self.users:
            # try the correct password
            self.assertTrue(users.check_login(self.db, nick, password), "Password check failed for nick %s" % nick)

            # and now incorrect
            self.assertFalse(users.check_login(self.db, nick, "badpassword"), "Bad Password check failed for nick %s" % nick)

    def test_check_login_unknown(self):
        """Test login for an unknown user id"""

        # check for an unknown user
        self.assertFalse(users.check_login(self.db, "unknownperson", "badpassword"), "Bad Password check failed for unknown user")

    def get_cookie_value(self, cookiename):
        """Get the value of a cookie from the bottle response headers"""

        headers = response.headerlist
        for h,v in headers:
            if h == 'Set-Cookie':
                cookie = SimpleCookie(v)
                if cookiename in cookie:
                    return cookie[cookiename].value

        return None

    def test_generate_session(self):
        """The generate_session procedure makes a new session cookie
        to be returned to the client
       """

        # run tests for all test users
        for password, nick, avatar in self.users:

            users.generate_session(self.db, nick)
            # get the sessionid from the response cookie

            sessionid = self.get_cookie_value(users.COOKIE_NAME)

            self.assertFalse(sessionid is None)

            cursor = self.db.cursor()
            cursor.execute('select usernick from sessions where sessionid=?', (sessionid,))

            query_result = cursor.fetchone()
            if query_result is None:
                self.fail("No entry for session id %s in sessions table" % (sessionid,))

            self.assertEqual(nick, query_result[0])

    def test_generate_session_twice(self):
        """Test generate_session in the case when there is already
        a session in place for a user"""

        password, nick, avatar = self.users[0]

        # make a first session
        users.generate_session(self.db, nick)
        sessionid = self.get_cookie_value(users.COOKIE_NAME)
        self.assertFalse(sessionid is None)

        # now try to make a new session
        users.generate_session(self.db, nick)

        sessionid2 = self.get_cookie_value(users.COOKIE_NAME)

        # sessionid should be the same as before
        self.assertEqual(sessionid, sessionid2)

    def test_generate_session_invalid_user(self):
        """Test generate_session in the case when the user is not known"""

        sessionid = users.generate_session(self.db, "Unknown")
        self.assertEqual(sessionid, None, "Invalid user should return None from generate_session")

    def test_delete_session(self):
        """The delete_session procedure should remove all sessions for
        a given user in the sessions table.
        Test relies on working generate_session"""

        # run tests for all test users
        for passwd, nick, avatar in self.users:
            users.generate_session(self.db, nick)
            # now remove the session
            users.delete_session(self.db, nick)
            # now check that the session is not present
            cursor = self.db.cursor()
            cursor.execute('select sessionid from sessions where usernick=?', (nick,))
            rows = cursor.fetchall()
            self.assertEqual(rows, [], "Expected no results for sessions query from deleted session, got %s" % (rows,))

    def test_session_user(self):
        """The session_user procedure finds the name of the logged in
        user from the session cookie if present

        Test relies on working generate_session
        """

        # first test with no cookie
        nick_from_cookie = users.session_user(self.db)
        self.assertEqual(nick_from_cookie, None, "Expected None in case with no cookie, got %s" % str(nick_from_cookie))

        request.cookies[users.COOKIE_NAME] = 'fake sessionid'
        nick_from_cookie = users.session_user(self.db)

        self.assertEqual(nick_from_cookie, None, "Expected None in case with invalid session id, got %s" % str(nick_from_cookie))

        # run tests for all test users
        for password, nick, avatar in self.users:

            users.generate_session(self.db, nick)

            sessionid = self.get_cookie_value(users.COOKIE_NAME)

            request.cookies[users.COOKIE_NAME] = sessionid

            nick_from_cookie = users.session_user(self.db)

            self.assertEqual(nick_from_cookie, nick)


if __name__ == "__main__":
    unittest.main()