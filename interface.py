"""
Database Model interface for the COMP249 Web Application assignment

@author: steve cassidy
"""


def position_list(db, limit=10):
    """Return a list of positions ordered by date
    db is a database connection
    return at most limit positions (default 10)

    Returns a list of tuples  (id, timestamp, owner, title, location, company, description)
    """

    cur = db.cursor()
    cur.execute("SELECT * FROM positions ORDER BY timestamp DESC")
 
    rows = cur.fetchall()
    
    position_list_data = []
    for row in rows:
        position_list_data += [row]
    return position_list_data[:limit]



def position_get(db, id):
    """Return the details of the position with the given id
    or None if there is no position with this id

    Returns a tuple (id, timestamp, owner, title, location, company, description)

    """
    cur = db.cursor()
    cur.execute("SELECT * FROM positions WHERE id='{}'".format(id))
 
    rows = cur.fetchall()
    
    position_data = None
    for row in rows:
        position_data = row
        break
    return position_data



def position_add(db, usernick, title, location, company, description):
    """Add a new post to the database.
    The date of the post will be the current time and date.
    Only add the record if usernick matches an existing user

    Return True if the record was added, False if not."""

    cur = db.cursor()
    cur.execute("SELECT * FROM positions WHERE owner='{}'".format(usernick))
 
    rows = cur.fetchall()

    if rows:
        cur.execute("INSERT INTO positions (owner, title, location, company, description) VALUES ('{}','{}','{}','{}','{}')".format(usernick, title, location, company, description))
        return True 
    return False




