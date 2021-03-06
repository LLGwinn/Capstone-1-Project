""" User model tests """

# to run:
#   python3 -m unittest tests/test_user_model.py

import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, User_Favorites

# Specify test database
os.environ['DATABASE_URL'] = "postgresql:///relocation-asst-test"

from app import app

# Create tables
db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    """ Test User model """

    def setUp(self):
        """ Delete any old data, create test clients, add sample data """

        User.query.delete()
        User_Favorites.query.delete()

        db.session.commit()

        self.client = app.test_client()

        user1 = User.register('testuser1','testpw1', 'test1@test.com', 'Tampa', 'Florida')
        user1_id = 1000
        user1.id = user1_id

        user2 = User.register('testuser2','testpw2', 'test2@test.com', 'Newark', 'New Jersey')
        user2_id = 2000
        user2.id = user2_id

        db.session.commit()

        user1 = User.query.get(user1_id)
        user2 = User.query.get(user2_id)
        
        self.user1 = user1
        self.user2 = user2

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    #===== BASIC MODEL ================
    #==================================
    def test_user_model(self):

        user = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            user_city='Boston',
            user_state='Massachusetts'
        )

        db.session.add(user)
        db.session.commit()

        # Basic user set up works
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertEqual(user.password, 'HASHED_PASSWORD')
        self.assertEqual(user.user_city, 'Boston')
        self.assertEqual(user.user_state, 'Massachusetts')

        # User should have no favorites
        self.assertEqual(len(user.favorites), 0)

        # Representation is accurate
        self.assertEqual(str(user), f'<User #{user.id}: {user.username}>')

    #===== REGISTER ====================
    #==================================
    def test_good_register(self):
        user = User.register('testuser', 'testpw', 'test@test.com', 'Miami', 'Florida')
        user_id = 3000
        user.id = user_id
        db.session.commit()

        self.assertIsInstance(user, User)
        self.assertEqual(user.id, 3000)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertTrue(user.password.startswith('$2b$'))
        self.assertEqual(user.user_city, 'Miami')
        self.assertEqual(user.user_state, 'Florida')

    def test_no_username_register(self):
        """ Error if no username entered """
        user = User.register(None, 'testpw', 'test@test.com', 'Atlanta', 'Georgia')
        user_id = 3000
        user.id = user_id

        with self.assertRaises(exc.IntegrityError): db.session.commit()

    def test_no_email_register(self):
        """ Error if no email entered """
        user = User.register('testuser', 'testpw', None, 'Atlanta', 'Georgia')
        user_id = 3000
        user.id = user_id

        with self.assertRaises(exc.IntegrityError): db.session.commit()

    def test_no_password_register(self):
        """ Error if no password entered """
        with self.assertRaises(ValueError): 
            User.register('testuser', None, 'test@test.com', 'Atlanta', 'Georgia')
        
    def test_dup_username_register(self):
        """ Error if username already in use (testuser1 signed up in setup function) """
        user = User.register('testuser1', 'test@test.com', 'testpw', 'Atlanta', 'Georgia')
        user_id = 3000
        user.id = user_id
        
        with self.assertRaises(exc.IntegrityError): db.session.commit()

    #===== AUTHENTICATION ===============
    #====================================
    def test_good_authenticate(self):
        """ testuser1 signed up in setup function """
        user = User.authenticate('testuser1','testpw1')

        self.assertIsInstance(user, User)

    def test_bad_username_authenticate(self):
        """ testuser1 signed up in setup function """
        self.assertFalse(User.authenticate('testuser3', 'testpw1'))

    def test_bad_password_authenticate(self):
        """ testuser1 signed up in setup function """
        self.assertFalse(User.authenticate('testuser1', 'bad_pw'))
