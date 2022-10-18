from app import app
from models import db, User

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
