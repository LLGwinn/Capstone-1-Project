""" Seed database with sample data """

from app import db
from csv import DictReader
from models import Geocode, User, User_Favorites


db.session.close()
db.drop_all()
db.create_all()


# ADD CENSUS BUREAU CITIES LIST #########
with open('all-geocodes-v2020.csv') as geocodes:
    db.session.bulk_insert_mappings(Geocode, DictReader(geocodes))

db.session.commit()

####### ADD SAMPLE USERS ################
# Call User.register so it will hash the password before commit to db
sample_user1 = User.register('hpotter', 'patronus', 'harry@hogwarts.edu', 1)
sample_user2 = User.register('hgranger', 'expeliarmus', 'hermione@hogwarts.edu', 2)

db.session.commit()
