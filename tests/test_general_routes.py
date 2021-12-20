""" General View tests """

# to run:
#    FLASK_ENV=production python3 -m unittest test_general_routes.py

import os
from unittest import TestCase
from csv import DictReader

from models import db, connect_db, User, Geocode, User_Favorites

# Specify test database
os.environ['DATABASE_URL'] = "postgresql:///relocation-asst-test"

from app import app, CURR_USER_KEY

# Create tables
db.drop_all()
db.create_all()

# Add Census Bureau cities to Geocode table
with open('all-geocodes-v2020.csv') as geocodes:
    db.session.bulk_insert_mappings(Geocode, DictReader(geocodes))

db.session.commit()

app.config['WTF_CSRF_ENABLED'] = False

class GeneralViewTestCase(TestCase):
    """ Test views for home, login, register """

    def setUp(self):
        """ Create test client, add sample data """
        User.query.delete()
        User_Favorites.query.delete()

        self.client = app.test_client()

        user1 = User.register('testuser1','testpw1', 'test1@test.com', 100)
        user1_id = 1000
        user1.id = user1_id

        db.session.commit()

        user1 = User.query.get(user1_id)
        
        self.user1 = user1

        favorite1 = User_Favorites(user_id=self.user1.id, city_id=999)
        db.session.add(favorite1)
        db.session.commit()

        user1 = User.query.filter(User.id == user1.id).first()
        self.user1 = user1

        favorite1 = User_Favorites.query.filter(User_Favorites.id == favorite1.id).first()
        self.favorite1 = favorite1
               
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_no_session_show_home_page(self):
        """ Home page with no user logged in """

        with self.client as c:
            response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Log in', str(response.data))
        self.assertIn('Let Relocation Assistant get you the information you need.', str(response.data))

    def test_show_home_page(self):
        """ Home page with user logged in """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            response = self.client.get('/')

            self.assertEqual(response.status_code, 200)
            self.assertIn('Log out', str(response.data))
            self.assertIn('Let Relocation Assistant get you the information you need.', str(response.data))

    def test_show_registration_form(self):
        with self.client as c:

            response = self.client.get('/register')

            self.assertEqual(response.status_code, 200)
            self.assertIn('input type="text" class="form-control" id="username"', str(response.data))
            self.assertIn(' <button type="submit" class="btn btn-dark">Create Account</button>', str(response.data))
    
    def test_create_account(self):
        """ Actual account creation logic is tested in user model, this test looks for 
            proper HTML response 
        """
        with self.client as c:

            response = self.client.post('/register',
                                        data={'username':'testuser2',
                                              'password':'testpw2', 
                                              'email':'test2@test.com', 
                                              'city':'Tampa',
                                              'state':'12'},
                                        follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Log out', str(response.data))
            self.assertIn('Let Relocation Assistant get you the information you need.', str(response.data))

    def test_handle_login(self):
        """ Actual authentication logic is tested in user model, this test looks for 
            proper HTML response 
        """
        with self.client as c:

            response = self.client.post('/login',
                                        data={'username':'testuser1',
                                              'password':'testpw1'},
                                        follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Log out', str(response.data))
            self.assertIn('Let Relocation Assistant get you the information you need.', str(response.data))

    def test_handle_logout(self):
        with self.client as c:

            with c.session_transaction() as session:
                CURR_USER_KEY = self.user1.id
                session[CURR_USER_KEY] = self.user1.id
            
            response = self.client.get('/logout', follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn('Log in', str(response.data))
            self.assertIn('Let Relocation Assistant get you the information you need.', str(response.data))