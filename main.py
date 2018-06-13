__author__ = 'Steve Cassidy'

from bottle import Bottle, template, static_file

app = Bottle()

from interface import position_list, position_get

import sqlite3



@app.route('/')
def index(db):
    position_list_ = [(position[0],position[1],position[2],position[3],str(str(position[6])[:100])) for position in  position_list(db)]

    info = {
        'title': 'Home',
        'position_list': position_list_
    }

    return template('index', info)

@app.route('/positions/<id>')
def index(db,id):
    data = position_get(db, id)
    info = {
        'title': 'Position Info',
        'data': data
    }

    return template('position_info', info)

@app.route('/about/')
def index(db):

    info = {
        'title': 'About'
    }

    return template('about', info)

@app.route('/static/<filename:path>')
def static(filename):
    return static_file(filename=filename, root='static')





if __name__ == '__main__':

    from bottle.ext import sqlite
    from database import DATABASE_NAME
    # install the database plugin
    app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
    app.run(debug=True, port=8010)
