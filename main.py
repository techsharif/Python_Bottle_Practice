__author__ = 'Steve Cassidy'

from bottle import Bottle, template, static_file
from bottle import get, post, request, redirect
app = Bottle()

from interface import position_list, position_get, position_add

import sqlite3
from users import check_login, session_user, generate_session, delete_session


@app.route('/')
def index(db):
    position_list_ = [(position[0],position[1],position[2],position[3],str(str(position[6])[:100])) for position in  position_list(db)]
    form_data = '''
            <form action="/login" method="post" id="loginform">
                Nick: <input name="nick" type="text" />
                Password: <input name="password" type="password" />
                <input value="Login" type="submit" />
            </form>
        '''
    user = session_user(db)
    if user:

        form_data = '''
        Logged in as Bobalooba
        <br>
        

        <form action="/post" method="post" id="postform">
                company: <input name="company" type="text" />
                title: <input name="title" type="text" />
                location: <input name="location" type="text" />
                description: <input name="description" type="text" />
                
                <input value="Login" type="submit" />
            </form>

            <br>
            <form action="/logout" method="post" id="logoutform">
               
                <button name='logout' value="Login" type="submit" >logout </but
            </form>
        '''
    info = {
        'title': 'Home',
        'position_list': position_list_,
        'form_data': form_data,
        'fail':''
    }

    return template('index', info)

@app.route('/positions/<id>')
def position(db,id):
    data = position_get(db, id)
    info = {
        'title': 'Position Info',
        'data': data
    }

    return template('position_info', info)

@app.route('/about/')
def about(db):

    info = {
        'title': 'About'
    }

    return template('about', info)


@app.route('/login')
def login(db):
    info = {
        'title': 'Login'
    }
    return template('login', info)

@app.route('/login', method='POST')
def do_login(db):
    nick = request.forms.get('nick')
    password = request.forms.get('password')
    if check_login(db, nick, password):
        generate_session(db, nick)
        redirect("/")
    else:
        form_data = '''
            <form action="/login" method="post" id="loginform">
                Nick: <input name="nick" type="text" />
                Password: <input name="password" type="password" />
                <input value="Login" type="submit" />
            </form>
        '''
        info = {
                'title': 'Home',
                'position_list': [],
                'form_data': form_data,
                'fail':'Login Failed, please try again <hr>'
            }

        return template('index', info)

@app.route('/logout', method='POST')
def logout(db):
    delete_session(db,session_user(db))
    redirect("/")
    

@app.route('/post', method='POST')
def post_(db):
    usernick = session_user(db)
    company = request.forms.get('company')
    title = request.forms.get('title')
    location = request.forms.get('location')
    description = request.forms.get('description')
    position_add(db, usernick, title, location, company, description);
    redirect("/")

@app.route('/static/<filename:path>')
def static(filename):
    return static_file(filename=filename, root='static')





if __name__ == '__main__':

    from bottle.ext import sqlite
    from database import DATABASE_NAME
    # install the database plugin
    app.install(sqlite.Plugin(dbfile=DATABASE_NAME))
    app.run(debug=True, port=8010)
