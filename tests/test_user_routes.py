""" User View tests """

# to run:
#    FLASK_ENV=production python3 -m unittest tests/test_user_routes.py

import os, requests
from unittest import TestCase

from models import db, connect_db, User, User_Favorites

# Specify test database
os.environ['DATABASE_URL'] = "postgresql:///relocation-asst-test"

from app import app, CURR_USER_KEY

# Create tables
db.drop_all()
db.create_all()

db.session.commit()

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """ Test views for users """

    def setUp(self):
        """ Create test client, add sample data """
        User.query.delete()
        User_Favorites.query.delete()

        self.client = app.test_client()

        user1 = User.register('testuser1','testpw1', 'test1@test.com', '68818', '27')
        user1_id = 1000
        user1.id = user1_id

        user2 = User.register('testuser2','testpw2', 'test2@test.com', '00460', '01')
        user2_id = 2000
        user2.id = user2_id

        db.session.commit()

        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)
        
        self.user1 = user1
        self.user2 = user2

        favorite1 = User_Favorites(user_id=self.user1.id, city_id='00124', state_id='01')
        db.session.add(favorite1)
        db.session.commit()

        user1 = User.query.filter(User.id == user1.id).first()
        self.user1 = user1

        user2 = User.query.filter(User.id == user2.id).first()
        self.user2 = user2

        favorite1 = User_Favorites.query.filter(User_Favorites.id == favorite1.id).first()
        self.favorite1 = favorite1
               
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def no_session_tests(self, res, msg, pg_heading):
        """ Test a path with no user logged in to session """
        self.assertEqual(res.status_code, 200)
        self.assertIn(f'{msg}', str(res.data))
        self.assertIn(f'{pg_heading}', str(res.data))

    def test_no_session_show_user_info(self):
        """ Display warning, redirect to login screen """
        with self.client as c:
            response = self.client.get(f'/users/{self.user1.id}', follow_redirects=True)

        msg = 'Please log in to view user profile.'
        pg_heading = 'Welcome back.'

        self.no_session_tests(response, msg, pg_heading)
    
    def test_show_user_info(self):
        """ Shows user profile info and favorite cities """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            city_data = requests.get(
                f'https://api.census.gov/data/2019/acs/acs5/subject?get=NAME&for=place:{self.user1.user_city}&in=state:{self.user1.user_state}'
            ).json()

            city = city_data[1][0].rsplit(',',1)[0].rsplit(' ',1)[0]

            response = self.client.get(f'/users/{self.user1.id}')

            self.assertEqual(response.status_code, 200)
            self.assertIn(f'Username: {self.user1.username}', str(response.data))
            self.assertIn(f'{city}', str(response.data))

    def test_no_session_edit_user(self):
        """ Display warning, redirect to login screen """
        with self.client as c:
            response = self.client.get(f'/users/{self.user1.id}/edit', follow_redirects=True)

        msg = 'Please log in to edit.'
        pg_heading = 'Welcome back.'

        self.no_session_tests(response, msg, pg_heading)
    
    def test_get_edit_user(self):
        """ Show form populated with user profile data on get request """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            response = self.client.get(f'/users/{self.user1.id}/edit')

        self.assertEqual(response.status_code, 200)
        self.assertIn('Edit information for', str(response.data))
        self.assertIn(f'{self.user1.username}', str(response.data))
        self.assertIn('value="test1@test.com"', str(response.data))

    def test_post_edit_user(self):
        """ Process and display profile change accurately """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            response = self.client.post(f'/users/{self.user1.id}/edit',
                                        data={'old_pw':'testpw1',
                                              'email':'changed@test.com'
                                              },
                                        follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(f'{self.user1.username}',str(response.data))
        self.assertIn('changed@test.com', str(response.data))

    def test_toggle_fav_city(self):
        """ Remove favorite from favorites table """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            response = self.client.post('/users/favs/add/00124/01', follow_redirects=True)

            self.assertEqual(response.status_code, 204)
            self.assertNotIn("fas fa-heart", str(response.data))
            self.assertNotIn(self.favorite1.id, [fav.id for fav in User_Favorites.query.all()])

    def test_no_session_delete_user(self):
        """ Display warning, redirect to login screen """
        with self.client as c:
            response = self.client.get(f'/users/{self.user1.id}/delete', follow_redirects=True)

        msg = 'Please log in to delete your account.'
        pg_heading = 'Welcome back.'

        self.no_session_tests(response, msg, pg_heading)

    def test_delete_user(self):
        """ Removes user from users table """
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            response = self.client.get(f'/users/{self.user1.id}/delete', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('Let Relocation Assistant get you the information you need.', str(response.data))
        self.assertNotIn(self.user1.id, [user.id for user in User.query.all()])
 