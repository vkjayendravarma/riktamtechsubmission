from src import db


class Groups(db.Document):
    name = db.StringField()
    description = db.StringField()
