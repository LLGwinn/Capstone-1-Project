""" Geocode model tests """

# to run:
#    python -m unittest test_geocode_model.py


import os
from unittest import TestCase
from csv import DictReader

from models import db, Geocode

# Specify test database
os.environ['DATABASE_URL'] = "postgresql:///relocation-asst-test"


from app import app

# Create tables
db.drop_all()
db.create_all()

# Add Census Bureau cities to Geocode table
with open('all-geocodes-v2020.csv') as geocodes:
    db.session.bulk_insert_mappings(Geocode, DictReader(geocodes))

db.session.commit()


class GeocodeModelTestCase(TestCase):
    """ Test Geocode model """

    #===== BASIC MODEL ================
    #==================================
    def test_message_model(self):

        geo = Geocode(id=99999, 
                      state='99', 
                      place='99999', 
                      name='Test City',
                      abbr='ZZ')

        db.session.add(geo)
        db.session.commit()

        self.assertEqual(geo.state, '99')
        self.assertEqual(geo.place, '99999')
        self.assertEqual(geo.name, 'Test City')
        self.assertEqual(geo.abbr, 'ZZ')
        self.assertEqual(geo.id, 99999)

        # Representation is accurate
        self.assertEqual(str(geo), f'<Geocode: state={geo.state}, place={geo.place}, name={geo.name}>')
