'''
Created on Mar 26, 2012

@author: steve
'''

import sqlite3
import json
import hashlib
import datetime
import random

# The database name
DATABASE_NAME = 'comp249.db'


def password_hash(password):
    """Return a one-way hashed version of the password suitable for
    storage in the database"""

    return hashlib.sha1(password.encode()).hexdigest()


def create_tables(db):
    """Create and initialise the database tables
    This will have the effect of overwriting any existing
    data."""

    sql = """
DROP TABLE IF EXISTS users;
CREATE TABLE users (
       nick text unique primary key,
       password text,
       avatar text
);

DROP TABLE IF EXISTS sessions;
CREATE TABLE sessions (
        sessionid text unique primary key,
        usernick text,
        FOREIGN KEY(usernick) REFERENCES users(nick)
);

DROP TABLE IF EXISTS positions;
CREATE TABLE positions (
        id integer unique primary key autoincrement,
        timestamp text default CURRENT_TIMESTAMP,
        owner text,
        title text,
        location text, 
        company text,
        description text,
        FOREIGN KEY(owner) REFERENCES users(nick)
);
"""

    db.executescript(sql)
    db.commit()


def sample_data(db):
    """Generate some sample data for testing the web
    application. Erases any existing data in the
    database
    Returns the list of users and the list of positions
    that are inserted into the database"""

    #  pass,   nick             avatar
    users = [('bob', 'Bobalooba', 'http://robohash.org/bob'),
             ('jim', 'Jimbulator', 'http://robohash.org/jim'),
             ('mary', 'Contrary', 'http://robohash.org/mary'),
             ('jb', 'Bean', 'http://robohash.org/jb'),
             ('mandible', 'Mandible', 'http://robohash.org/mandible'),
             ('bar', 'Barfoo', 'http://robohash.org/bar'),
    ]
    #  Robots lovingly delivered by Robohash.org

    cursor = db.cursor()
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM positions")

    # create one entry for each user
    for password, nick, avatar in users:
        sql = "INSERT INTO users (nick, password, avatar) VALUES (?, ?, ?)"
        cursor.execute(sql, (nick, password_hash(password), avatar))

    # read sample job data from positions.json
    positions = []
    with open('positions.json') as fd:
        joblist = json.load(fd)
    for job in joblist:
        sql = """
INSERT INTO positions 
  (timestamp, owner, title, location, company, description) 
VALUES
  (?,?,?,?,?,?)"""
        # need to parse the date string before inserting into the database
        timestamp = datetime.datetime.strptime(job['created_at'], "%a %b %d %H:%M:%S UTC %Y")
        # choose a random owner for the job
        owner = random.choice(users)
        data = (timestamp, owner[1], job['title'], job['location'],
                job['company'], job['description'])
        positions.append(data)

        cursor.execute(sql, data)

    db.commit()

    return users, positions


if __name__=='__main__':
    # if we call this script directly, create the database and make sample data
    db = sqlite3.connect(DATABASE_NAME)
    create_tables(db)
    sample_data(db)