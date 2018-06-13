__author__ = 'Steve Cassidy'

from bottle import Bottle, template, static_file

app = Bottle()


@app.route('/')
def index(db):

    info = {
        'title': 'Home'
    }

    return template('index', info)

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
