"""
Created on Mar 26, 2012

@author: steve
"""

# this variable MUST be used as the name for the cookie used by this application
COOKIE_NAME = 'sessionid'
from database import password_hash
import uuid
from bottle import response, request


def check_login(db, usernick, password):
    """returns True if password matches stored"""
    password = password_hash(password) 
    query = f'''SELECT * FROM users where nick='{usernick}' and password='{password}' '''
    cursor = db.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    if rows:
        return True
    else:
        return False


def generate_session(db, usernick):
    """create a new session and add a cookie to the response object (bottle.response)
    user must be a valid user in the database, if not, return None
    There should only be one session per user at any time, if there
    is already a session active, use the existing sessionid in the cookie
    """


    key = str(uuid.uuid4())
    cur = db.cursor()

    # valid user check
    cur.execute("SELECT nick FROM users WHERE nick=?", (usernick,))
    row = cur.fetchone()

    if not row:
        return None

    # check if session already exists 
    cur.execute("SELECT sessionid FROM sessions WHERE usernick=?", (row[0],))

    row = cur.fetchone()


    if row:
        return row[0]

    # store this new session key in the database with no likes in the value
    cur.execute(f"INSERT INTO sessions VALUES ('{key}', '{usernick}')")
    db.commit()

    response.set_cookie(COOKIE_NAME, key)

    return key


def delete_session(db, usernick):
    """remove all session table entries for this user"""
    cur = db.cursor()
    cur.execute(f"DELETE FROM sessions WHERE usernick='{usernick}'")
    db.commit()


def session_user(db):
    """try to
    retrieve the user from the sessions table
    return usernick or None if no valid session is present"""

    key = request.get_cookie(COOKIE_NAME)

    cur = db.cursor()
    cur.execute("SELECT usernick FROM sessions WHERE sessionid=?", (key,))

    row = cur.fetchone()


    if row:
        return row[0]
    else:
        None


