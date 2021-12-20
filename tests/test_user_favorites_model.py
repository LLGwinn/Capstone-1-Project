""" User_Favorites model tests """

# to run:
#    python3 -m unittest tests/test_user_favorites_model.py

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

class User_FavoritesModelTestCase(TestCase):
    """ Test User_Favorites model """

    def setUp(self):
        """ Create test users and add sample data """

        User.query.delete()
        User_Favorites.query.delete()

        db.session.commit()

        self.client = app.test_client()

        user1 = User.register('testuser1','testpw1', 'test1@test.com', '00124','01')
        user1_id = 1000
        user1.id = user1_id

        user2 = User.register('testuser2','testpw2', 'test2@test.com', '00460','01')
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
    def test_user_favorites_model(self):
        fav = User_Favorites(user_id=self.user1.id, city_id='00484', state_id='01')
        db.session.add(fav)
        db.session.commit()

        self.assertEqual(fav.user_id, self.user1.id)
        self.assertEqual(fav.city_id, '00484')

    #===== USER RELATIONSHIP ==========
    #==================================
    def test_user_relationship(self):
        fav = User_Favorites(user_id=self.user1.id, city_id='00484', state_id='01')
        db.session.add(fav)
        db.session.commit()

        self.assertEqual(len(self.user1.favorites), 1)
        self.assertEqual(len(self.user2.favorites), 0)

        



