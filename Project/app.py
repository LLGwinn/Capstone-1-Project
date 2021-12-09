import os, requests

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from requests.api import get
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, User_Favorites, Geocode
from forms import UserAddForm, LoginForm, UserEditForm

CURR_USER_KEY = 'curr_user'

app = Flask(__name__)

# Get DB_URI from environ variable.
# If not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///relocation_asst'))
    # 'postgresql:///blogly').replace("postgres://", "postgresql://", 1

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '12345')
toolbar = DebugToolbarExtension(app)

connect_db(app)


states = db.session.query(
        Geocode.state.distinct(),Geocode.abbr).order_by(Geocode.abbr).all()

def get_state_abbr(state_code):
    """ Find the state abbreviation that matches the given state code """

    for code, abbr in states:
        if state_code == code:
            return abbr


##############################################################################
# API Calls
def get_weather(city):
    """ Access OpenWeather API for current weather """
    res = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city}&units=imperial&appid=38b23dca5266fbaec142ba9c8f6ccac8'
        )
    data = res.json()

    icon_code = data['weather'][0]['icon']
    conditions = data['weather'][0]['description']
    temp = data['main']['temp']

    return {'icon':icon_code, 'conditions':conditions, 'temp':temp}

def get_census_data(city, state):
    """ Access U.S. Census American Community Survey """

    base_url = 'https://api.census.gov/data/2019/acs/acs5/profile?get=NAME,'

    geocode = Geocode.query.filter(
        Geocode.name.like(f'{city}%'),
        Geocode.state==state
        ).first()

    if geocode:
        state = geocode.state
        place = geocode.place
        vars = {
            'pop':'DP05_0001E', 
            'age':'DP05_0018E', 
            'inc':'DP03_0062E', 
            'home':'DP04_0089E'
            }

        query_url = base_url + \
            (f'{vars["pop"]},{vars["age"]},{vars["inc"]},{vars["home"]}&for=place:{place}&in=state:{state}')

        response = requests.get(query_url)
        data = response.json()

        return data
    
    else:
        return False

##############################################################################
# Register/login/logout

@app.before_request
def add_user_to_g():
    """ If a user is logged in, add curr user to Flask global """
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def login(user):
    """ Log in user """
    session[CURR_USER_KEY] = user.id

def logout():
    """ Logout user """
    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)
        flash("Logout successful", 'success')


@app.route('/register')
def show_registration_form():
    """ Create new user, add to DB, log user in. 
        If form validation fails, present form.
        If username is already in db, flash message and re-render form.
    """

    return render_template('register.html', states=states)

@app.route('/register', methods=['POST'])
def create_account():

    city_id = Geocode.query.filter(Geocode.name.like(f'{request.form["city"]}%'), 
                                    Geocode.state==request.form['state']).first()

    try:
        user = User.register(request.form['username'],
                             request.form['password'],
                             request.form['email'],
                             city_id.id
        )
        print(user)
        db.session.commit()

    except IntegrityError:
        flash("Username already taken", 'danger')
        return render_template('register.html')

    login(user)
    return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    """ Handle user login """

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            login(user)
            flash(f"Welcome, {user.username}!", 'success')
            return redirect('/')

        flash("Invalid credentials", 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def handle_logout():
    """ Handle logout of user """

    logout()

    return redirect('/login')

# ##############################################################################
# # Homepage

@app.route('/')
def show_homepage():

    return render_template('home.html', states=states)


##############################################################################
# User routes:
# @app.route('/user/<int:user_id>')
# def show_user_info(user_id):
#     """ Show user profile information and favorite cities """


# @app.route('user/<int:user_id>/edit', methods=['POST'])
# def edit_user(user_id):
#     """ Edit user profile information """


##############################################################################
# City routes: 
@app.route('/cities/compare')
def compare_cities():
    """ Show data for two cities""" 

    curr_city = request.args.get('curr-city')
    curr_state = request.args.get('curr-state')
    dest_city = request.args.get('dest-city')
    dest_state = request.args.get('dest-state')

    curr_weather = get_weather(curr_city)
    dest_weather = get_weather(dest_city)

    curr_census_data = get_census_data(curr_city, curr_state)
    dest_census_data = get_census_data(dest_city, dest_state)

    if curr_census_data:
        curr_census = {
            "pop":curr_census_data[1][1],
            "age":curr_census_data[1][2],
            "inc":curr_census_data[1][3],
            "home":curr_census_data[1][4]
        }
    else:
        curr_census = {
            "pop":"not found",
            "age":"not found",
            "inc":"not found",
            "home":"not found"
            }

    if dest_census_data:
        dest_census = {
            "pop":dest_census_data[1][1],
            "age":dest_census_data[1][2],
            "inc":dest_census_data[1][3],
            "home":dest_census_data[1][4]
            }
    else:
        dest_census = {
            "pop":"not found",
            "age":"not found",
            "inc":"not found",
            "home":"not found"
            }

    for item in curr_census:
        if curr_census[item] == '-888888888':
            curr_census[item] = "no data available"

    for item in dest_census:
        if dest_census[item] == '-888888888':
            dest_census[item] = "no data available"
        
    curr_data = {"name":curr_city,
                 "abbr": get_state_abbr(curr_state),
                 "census":curr_census, 
                 "weather":curr_weather}
    dest_data = {"name":dest_city,
                 "abbr": get_state_abbr(dest_state),
                 "census":dest_census,
                 "weather":dest_weather}

    return render_template('comparison.html', curr=curr_data, dest=dest_data)



#################################################
# examples
#################################################
# @app.route('/users/<int:user_id>')
# def users_show(user_id):
#     """ Show user profile """

#     user = User.query.get_or_404(user_id)

#     # snagging messages in order from the database;
#     # user.messages won't be in order by default
#     messages = (Message
#                 .query
#                 .filter(Message.user_id == user_id)
#                 .order_by(Message.timestamp.desc())
#                 .limit(100)
#                 .all())
#     return render_template('users/show.html', user=user, messages=messages)

# @app.route('/users/add_like/<int:msg_id>', methods=['POST'])
# def toggle_like_message(msg_id):
#     """ Add or remove 'like' from likes table """
#     msg = Likes.query.filter(Likes.message_id==msg_id).first()

#     # if message is already liked, unlike
#     if msg:
#         db.session.delete(msg)
#     # if message not liked already, create a new like
#     else:
#         new_like = Likes(message_id=msg_id, user_id=g.user.id)
#         db.session.add(new_like)

#     db.session.commit()

#     return redirect('/')

# @app.route('/users/<int:user_id>/likes')
# def users_likes(user_id):
#     """ Show list of liked messages for this user """
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
    
#     return render_template('users/show.html', user=user, messages=user.likes)

    
# @app.route('/users/<int:user_id>/profile', methods=["GET", "POST"])
# def profile(user_id):
#     """ Update profile for current user """
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
#     form = UserEditForm(obj=user)

#     if form.validate_on_submit():
#         authorized = User.authenticate(form.username.data, form.password.data)

#         if authorized:
#             user.username = form.username.data
#             user.email = form.email.data
#             user.image_url = form.image_url.data
#             user.header_image_url = form.header_image_url.data
#             user.bio = form.bio.data

#             db.session.add(user)
#             db.session.commit()

#             return redirect(f'/users/{user_id}')

#         else:
#             flash("Username/password incorrect", "danger")
#             return redirect("/")

#     return render_template('/users/edit.html', user=user, form=form)


# @app.route('/users/delete', methods=["POST"])
# def delete_user():
#     """Delete user."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     do_logout()

#     db.session.delete(g.user)
#     db.session.commit()

#     return redirect("/signup")

# ##############################################################################
# # Messages routes:

# @app.route('/messages/new', methods=["GET", "POST"])
# def messages_add():
#     """Add a message:

#     Show form if GET. If valid, update message and redirect to user page.
#     """

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     form = MessageForm()

#     if form.validate_on_submit():
#         msg = Message(text=form.text.data)
#         g.user.messages.append(msg)
#         db.session.commit()

#         return redirect(f"/users/{g.user.id}")

#     return render_template('messages/new.html', form=form)


# @app.route('/messages/<int:message_id>', methods=["GET"])
# def messages_show(message_id):
#     """Show a message."""

#     msg = Message.query.get(message_id)
#     return render_template('messages/show.html', message=msg)


# @app.route('/messages/<int:message_id>/delete', methods=["POST"])
# def messages_destroy(message_id):
#     """Delete a message."""

#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     msg = Message.query.get(message_id)
#     db.session.delete(msg)
#     db.session.commit()

#     return redirect(f"/users/{g.user.id}")

# ##############################################################################
# # Homepage and error pages

# @app.route('/')
# def homepage():
#     """Show homepage:

#     - anon users: no messages
#     - logged in: 100 most recent messages of followed_users
#     """
#     if g.user:
#         users_followed = [f_user.id for f_user in g.user.following]

#         messages = (Message
#                     .query
#                     .filter((Message.user_id==g.user.id) | (Message.user_id.in_(users_followed)))
#                     .order_by(Message.timestamp.desc())
#                     .limit(100)
#                     .all())

#         return render_template('home.html', messages=messages)

#     else:
#         return render_template('home-anon.html')


# ##############################################################################
# # Turn off all caching in Flask
# #   (useful for dev; in production, this kind of stuff is typically
# #   handled elsewhere)
# #
# # https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

# @app.after_request
# def add_header(req):
#     """Add non-caching headers on every request."""

#     req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
#     req.headers["Pragma"] = "no-cache"
#     req.headers["Expires"] = "0"
#     req.headers['Cache-Control'] = 'public, max-age=0'
#     return req

# @app.route('/users')
# def list_users():
#     """Page with listing of users.

#     Can take a 'q' param in querystring to search by that username.
#     """

#     search = request.args.get('q')

#     if not search:
#         users = User.query.all()
#     else:
#         users = User.query.filter(User.username.like(f"%{search}%")).all()

#     return render_template('users/index.html', users=users)


# @app.route('/users/<int:user_id>')
# def users_show(user_id):
#     """ Show user profile """

#     user = User.query.get_or_404(user_id)

#     # snagging messages in order from the database;
#     # user.messages won't be in order by default
#     messages = (Message
#                 .query
#                 .filter(Message.user_id == user_id)
#                 .order_by(Message.timestamp.desc())
#                 .limit(100)
#                 .all())
#     return render_template('users/show.html', user=user, messages=messages)


# @app.route('/users/add_like/<int:msg_id>', methods=['POST'])
# def toggle_like_message(msg_id):
#     """ Add or remove 'like' from likes table """
#     msg = Likes.query.filter(Likes.message_id==msg_id).first()

#     # if message is already liked, unlike
#     if msg:
#         db.session.delete(msg)
#     # if message not liked already, create a new like
#     else:
#         new_like = Likes(message_id=msg_id, user_id=g.user.id)
#         db.session.add(new_like)

#     db.session.commit()

#     return redirect('/')

# @app.route('/users/<int:user_id>/likes')
# def users_likes(user_id):
#     """ Show list of liked messages for this user """
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
    
#     return render_template('users/show.html', user=user, messages=user.likes)

    
# @app.route('/users/<int:user_id>/profile', methods=["GET", "POST"])
# def profile(user_id):
#     """ Update profile for current user """
#     if not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     user = User.query.get_or_404(user_id)
#     form = UserEditForm(obj=user)

#     if form.validate_on_submit():
#         authorized = User.authenticate(form.username.data, form.password.data)

#         if authorized:
#             user.username = form.username.data
#             user.email = form.email.data
#             user.image_url = form.image_url.data
#             user.header_image_url = form.header_image_url.data
#             user.bio = form.bio.data

#             db.session.add(user)
#             db.session.commit()

#             return redirect(f'/users/{user_id}')

#         else:
#             flash("Username/password incorrect", "danger")
#             return redirect("/")

#     return render_template('/users/edit.html', user=user, form=form)