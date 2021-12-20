""" Seed database with sample data """

from app import db
from models import User


db.session.close()
db.drop_all()
db.create_all()


####### ADD SAMPLE USERS ################
# Call User.register so it will hash the password before commit to db
sample_user1 = User.register('hpotter', 'patronus', 'harry@hogwarts.edu', '00124', '01')
sample_user2 = User.register('hgranger', 'expeliarmus', 'hermione@hogwarts.edu', '68818', '27')

db.session.commit()
