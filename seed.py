from app import app
from models import db, User, Feedback

db.drop_all()
db.create_all()


users = [
    User.register(username="bonsaibooy", password="littletrees",
                  email="johnathan.booy@gmail.com", first_name="Johnathan", last_name="Booy"),
    User.register(username="pumpkinspice", password="everythingnice",
                  email="mackay.meganlea@gmail.com", first_name="Megan", last_name="Mackay")
]

for user in users:
    db.session.add(user)

db.session.commit()

feedback = [
    Feedback(username="bonsaibooy", title="Not enough trees!",
             content="I joined hoping to learn more about bonsai! Very disappointed."),
    Feedback(username="bonsaibooy", title="Good user experience",
             content="Well done on that front, but again. Where are the trees?"),
    Feedback(username="pumpkinspice", title="What is this site?",
             content="Like literally.... what?")
]

for fb in feedback:
    db.session.add(fb)

db.session.commit()
