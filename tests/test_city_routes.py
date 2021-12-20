""" City View tests """

# to run:
#    FLASK_ENV=production python3 -m unittest tests/test_city_routes.py

import os
from unittest import TestCase

from models import db, connect_db, User, User_Favorites

# Specify test database
os.environ['DATABASE_URL'] = "postgresql:///relocation-asst-test"

from app import app, CURR_USER_KEY

# Create tables
db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class CityViewTestCase(TestCase):
    """ Test views for cities """

    def setUp(self):
        """ Create test client, add sample data """
        User.query.delete()
        User_Favorites.query.delete()

        self.client = app.test_client()
     
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_compare_cities(self):
        """ Shows data from Tampa, FL and Miami, FL """
        with self.client as c:

            response = self.client.post('/cities/compare',
                                        data={'curr-city':'Tampa',
                                              'curr-state':'12',
                                              'curr-abbr':'US-FL',
                                              'dest-city':'Miami',
                                              'dest-state':'12'
                                            }, follow_redirects=True
                                        )

            self.assertEqual(response.status_code, 200)
            self.assertIn('Tampa', str(response.data))
            self.assertIn('Miami', str(response.data))
            self.assertIn('Population', str(response.data))
            self.assertIn('img src="http://openweathermap.org/img/', str(response.data))

    def test_get_advice(self):
        """ Shows advice for comparison with accurate calculations """
        with self.client as c:
            with c.session_transaction() as sess:
                sess['curr_data'] = {"name":'Tampa',
                            "abbr": 'FL',
                            "census":{"id":'99999',
                                    "pop":'99999', 
                                    "age":'99999',
                                    "inc":'100000', 
                                    "home":'100000',
                                    "state":'99',
                                    "place":'99999'}, 
                            "weather":{'icon':'zzz', 'temp':999}
                            }
                sess['dest_data'] = {"name":'Miami',
                            "abbr": 'FL',
                            "census":{"id":'77777',
                                    "pop":'77777', 
                                    "age":'77777',
                                    "inc":'125000', 
                                    "home":'175000',
                                    "state":'77',
                                    "place":'77777'}, 
                            "weather":{'icon':'yyy', 'temp':777}
                            }
            response = self.client.get('/cities/advice') 

            self.assertEqual(response.status_code, 200)
            self.assertIn('There are lots of things to consider', str(response.data))
            self.assertIn('Tampa', str(response.data))
            self.assertIn('Miami', str(response.data))
            self.assertIn('Average incomes are', str(response.data))
            self.assertIn('25%', str(response.data))
            self.assertIn('75%', str(response.data))
