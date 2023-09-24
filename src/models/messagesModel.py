from src import db
import datetime

class Messages(db.Document):
    date = db.DateTimeField(default=datetime.datetime.utcnow())
    userId = db.ObjectIdField(required=True)
    body = db.StringField(required=True)
    groupId = db.ObjectIdField(required=True)
    