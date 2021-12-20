import os, requests
import keys

from flask import Flask, render_template, request, flash, redirect, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from requests.api import get
from sqlalchemy.exc import IntegrityError
from flask_bcrypt import Bcrypt

from models import db, connect_db, User, User_Favorites
from forms import LoginForm, UserEditForm

CURR_USER_KEY = 'curr_user'

app = Flask(__name__)

# Get DB_URI from environ variable.
# If not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///relocation_asst').replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', '12345')
toolbar = DebugToolbarExtension(app)

connect_db(app)

bcrypt = Bcrypt()

def analyze(curr, dest):
    """ Compare income and home value data from both cities """

    inc_ratio = round(
        (int(dest['census']['inc'])/int(curr['census']['inc'])), 
        2)

    home_ratio = round(
       (int(dest['census']['home'])/int(curr['census']['home'])),
        2)

    # positive income move, home prices same or more within 5% of income ratio
    # (more money, same buying power)
    if (inc_ratio >= 1) and ((.98 <= home_ratio <= 1.02) or ((inc_ratio - .05) <= home_ratio <= inc_ratio + .05)):
        income = 'higher'
        inc_percent = round((inc_ratio - 1) * 100)
        home = f"are about the same or would increase by about the same percentage ({round(100 - (home_ratio * 100))})%"
        msg = 'This could be a good move for you!'

    # positive income move, home prices lower
    # (more money, more buying power)
    if (inc_ratio >= 1) and ((home_ratio < 1)):
        income = 'higher'
        inc_percent = round((inc_ratio - 1) * 100)
        home = f'are {round(100 - (home_ratio * 100))}% lower'
        msg = 'This is definitely a good move for you!'

    # positive income move, home prices higher at least 5% more than income ratio
    # (more money, less buying power)
    elif (inc_ratio >= 1) and (home_ratio > (inc_ratio + .05)):
        income = 'higher'
        inc_percent = round((inc_ratio - 1) * 100)
        home = f'would be {round((home_ratio -1) * 100)}% more'
        msg = 'Your buying power is lower. Not a good move.'

    # positive income move, home prices higher but not more than income ratio
    # #(more money, a little more buying power)
    elif (inc_ratio >=1) and (1.02 < home_ratio <= (inc_ratio + .05)):
        income = 'higher'
        inc_percent = round((inc_ratio - 1) * 100)
        home = f'would only be {round((home_ratio -1) * 100)}% more'
        msg = 'Your buying power is a little better. How important is this move?'

    # negative income move, home prices same or more within 5% of income ratio
    # (less money, same buying power)
    elif (inc_ratio < 1) and ((.98 <= home_ratio <= 1.02) or ((inc_ratio - .05) <= home_ratio <= inc_ratio + .05)):
        income = 'lower'
        inc_percent = round(100 - (inc_ratio * 100))
        home = f'are about the same or would decrease by about the same percentage ({round(100 - (home_ratio * 100))})%'
        msg = 'Can you afford to take a pay cut and keep the same expenses?'

    # negative income move, home prices lower
    # (less money, more buying power)
    elif (inc_ratio < 1) and (home_ratio <= 1):
        income = 'lower'
        inc_percent = round(100 - (inc_ratio * 100))
        home = f'would be {round(100 - (home_ratio * 100))}% lower'
        msg = 'Do you want to earn less income even if housing prices are lower? How important is this move?'

    # negative income move, home prices higher at least 5% higher than income ratio
    # (less money, less buying power)
    elif (inc_ratio < 1) and (home_ratio > (inc_ratio + .05)):
        income = 'lower'
        inc_percent = round(100 - (inc_ratio * 100))
        home = f'would be {round((home_ratio - 1) * 100)}% more'
        msg = 'Lower pay and less buying power. Terrible move!'
  
    return ({'inc':income, 'inc_perc':inc_percent, 'home':home, 'msg':msg }) 

##############################################################################
# API Calls
def get_weather(city, state):
    """ Access OpenWeather API for current weather """
    state_abbr = state[3:]

    res = requests.get(
        f'https://api.openweathermap.org/data/2.5/weather?q={city},{state_abbr},US&units=imperial&appid={keys.weather_key}'
        )
    data = res.json()

    if data['cod'] == '404':
        return{'icon':'01n', 'temp':None}
    else:
        icon_code = data['weather'][0]['icon']
        temp = data['main']['temp']
        return {'icon':icon_code, 'temp':temp}

def get_census_codes(city, state):
    """ Get state and place codes for census api """

    all_states = requests.get(
        'https://api.census.gov/data/2019/acs/acs5/subject?get=NAME&for=state:*').json()
 
    state_code = [item[1] for item in all_states if item[0] == state][0]

    # Bug in the geocoder lists New York as New York City. Grr.
    if city == 'New York City':
        city = 'New York'
 
    cities = requests.get(
        f'https://api.census.gov/data/2019/acs/acs5/subject?get=NAME&for=place:*&in=state:{state_code}'
    ).json()

    for item in cities:
        census_city_name = item[0].rsplit(',',1)[0].rsplit(' ',1)[0]
        if census_city_name==city:
            place_code = item[2]
            state_code = item[1]
            return {'place':place_code,'state':state_code}

    return False

def get_census_data(city, state):
    """ Access U.S. Census American Community Survey """

    base_url = 'https://api.census.gov/data/2019/acs/acs5/profile?get=NAME,'
    vars = {
            'pop':'DP05_0001E', 
            'age':'DP05_0018E', 
            'inc':'DP03_0062E', 
            'home':'DP04_0089E'
            }

    query_url = base_url + \
             (f'{vars["pop"]},{vars["age"]},{vars["inc"]},{vars["home"]}&for=place:{city}&in=state:{state}')
    
    response = requests.get(query_url).json()

    city_data = {"pop":response[1][1], 
                 "age":response[1][2],
                 "inc":response[1][3], 
                 "home":response[1][4],
                 "state":state,
                 "place":city}

    # if census has no data for a particular variable for the specified city
    for item in city_data:
        if city_data[item] == '-888888888':
            city_data[item] = "no data available"

    return city_data

##############################################################################
# Register/login/logout

def login(user):
    """ Log in user """
    session[CURR_USER_KEY] = user.id

def logout():
    """ Logout user """
    if CURR_USER_KEY in session:
        session.pop(CURR_USER_KEY)

@app.before_request
def add_user_to_g():
    """ If a user is logged in, add curr user to Flask global """
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

@app.route('/register')
def show_registration_form():
 
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def create_account():
    """ Create new user, add to DB, log user in. 
        If username is already in db, flash message and re-render form.
    """
    codes = get_census_codes(request.form['user-city'], request.form['user-state'])
    if not codes:
        flash(f"{request.form['user-city']} was not found in the US Census data. Please try a different city.",'danger')
        return redirect('/')

    city = codes['place']
    state = codes['state']

    try:
        user = User.register(request.form['username'],
                             request.form['password'],
                             request.form['email'],
                             city,
                             state
        )
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

    return redirect('/')

# ##############################################################################
# Homepage

@app.route('/')
def show_homepage():

    return render_template('home.html')

##############################################################################
# User routes:

@app.route('/users/<int:user_id>')
def show_user_info(user_id):
    """ Show user profile information and favorite cities """

    if not g.user:
        flash("Please log in to view user profile.", "danger")
        return redirect('/login')

    else:
        user = User.query.get(user_id)
        user_city_data = requests.get(
                f'https://api.census.gov/data/2019/acs/acs5/subject?get=NAME&for=place:{user.user_city}&in=state:{user.user_state}'
            ).json()

        user_city = user_city_data[1][0].rsplit(',',1)[0].rsplit(' ',1)[0]
        user_state = user_city_data[1][0].rsplit(', ')[1]

        favs = User_Favorites.query.filter(User_Favorites.user_id==user.id).all()
        favorites = []

        for item in favs:
            item_data = requests.get(
                f'https://api.census.gov/data/2019/acs/acs5/subject?get=NAME&for=place:{item.city_id}&in=state:{item.state_id}'
            ).json()

            city_name = item_data[1][0].rsplit(',',1)[0].rsplit(' ',1)[0]
            state_name = item_data[1][0].rsplit(', ')[1]

            favorites.append({'id':item.id, 'city':city_name, 'state':state_name})
  
        return render_template('user_info.html', 
                                favorites=favorites, user=user, user_city=user_city, user_state=user_state)

@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """ Edit user profile information """

    if not g.user:
        flash("Please log in to edit.", "danger")
        return redirect('/login')

    else:
        user = User.query.get_or_404(user_id)
        form = UserEditForm()

        if form.validate_on_submit():
            authorized = User.authenticate(g.user.username, form.old_pw.data)

            if authorized:
                user.username = g.user.username
                if form.new_pw.data:
                    new_hashed_pw = bcrypt.generate_password_hash(form.new_pw.data).decode('UTF-8')
                    user.password = new_hashed_pw
                if form.email.data:
                    user.email = form.email.data
                if request.form['user-city']:
                    codes = get_census_codes(request.form['user-city'], request.form['user-state'])
                    if not codes:
                        flash(f"{request.form['user-city']} was not found in the US Census data. Please try a different city.",'danger')
                        return redirect('/')

                    user.user_city = codes['place']
                    user.user_state = codes['state']

                db.session.add(user)
                db.session.commit()

                return redirect(f'/users/{user.id}')

            else:
                flash("Username/password incorrect", "danger")
                return redirect("/")

        return render_template('user_edit.html', user=user, form=form)

@app.route('/users/favs/add/<city>/<state>', methods=['POST'])
def toggle_fav_city(city, state):
    """ Add or remove city from favorites table """

    if not g.user:
        flash("Please log in to add a favorite.", "danger")
        return redirect('/login')

    else:
        user = g.user

        fav = User_Favorites.query.filter(User_Favorites.city_id==city,
                                          User_Favorites.state_id==state,
                                          User_Favorites.user_id==user.id).one_or_none()

        # if city is already favorited, unfavorite
        if fav:
            db.session.delete(fav)
        # if city not favorited already, create a new favorite
        else:
            new_favorite = User_Favorites(user_id=user.id,
                                          city_id=city,
                                          state_id=state
                                          )
            db.session.add(new_favorite)

        db.session.commit()

        return redirect('', 204)

@app.route('/users/favs/delete/<int:id>', methods=['DELETE'])
def delete_favorite(id):
    """ Delete user favorite when user_info page trash button clicked """

    favorite = User_Favorites.query.get_or_404(id)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify(message='deleted')

@app.route('/users/<int:user_id>/delete')
def delete_user(user_id):
    """ Delete user from db """

    if not g.user:
        flash("Please log in to delete your account.", "danger")
        return redirect('/login')

    else:
        logout()
        db.session.delete(g.user)
        db.session.commit()

        return redirect("/")

##############################################################################
# City routes:
 
@app.route('/cities/compare', methods=['POST'])
def compare_cities():
    """ Show data for two cities""" 

    curr_city = request.form['curr-city']
    curr_state = request.form['curr-state']
    curr_abbr = request.form['curr-abbr']
    dest_city = request.form['dest-city']
    dest_state = request.form['dest-state']
    dest_abbr = request.form['dest-abbr']

    if not curr_city or not curr_state or not dest_city or not dest_state:
        flash('Uh oh. Looks like some input data was missing. Please try again.', 'danger')
        return redirect('/')

    curr_codes = get_census_codes(curr_city, curr_state)
    if not curr_codes:
        flash(f'{curr_city} was not found in the US Census data. Please try a different city.','danger')
        return redirect('/')
    dest_codes = get_census_codes(dest_city, dest_state)
    if not dest_codes:
        flash(f'{dest_city} was not found in the US Census data. Please try a different city.','danger')
        return redirect('/')

    curr_census_data = get_census_data(curr_codes['place'], curr_codes['state'])
    dest_census_data = get_census_data(dest_codes['place'], dest_codes['state'])

    if curr_census_data['state'] != '00':
        curr_weather = get_weather(curr_city, curr_abbr)
    else:
        curr_weather = {'icon':'01n', 'temp':None}

    if dest_census_data['state'] != '00':
        dest_weather = get_weather(dest_city, dest_abbr)
    else:
        dest_weather = {'icon':'01n', 'temp':None}
        
    curr_data = {"name":curr_city,
                 "abbr": curr_abbr[3:],
                 "census":curr_census_data, 
                 "weather":curr_weather}
    dest_data = {"name":dest_city,
                 "abbr": dest_abbr[3:],
                 "census":dest_census_data,
                 "weather":dest_weather}

    if g.user:
        favorites = [city.id for city in g.user.favorites]
    else:
        favorites = []

    session['curr_data'] = curr_data
    session['dest_data'] = dest_data

    return render_template('comparison.html', curr=curr_data, dest=dest_data, favorites=favorites)

@app.route('/cities/advice')
def get_advice():
    """ Show user quick analysis of two cities """

    curr = session['curr_data']
    dest = session['dest_data']

    results = analyze(curr, dest)

    return render_template('advice.html', results=results, curr=curr, dest=dest)

@app.route('/map_search')
def show_search():
    token = keys.mapbox_token
    return render_template('map_search.html', token=token)


# ##############################################################################
# # Turn off all caching in Flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
