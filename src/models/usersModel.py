from src import db

class User(db.Document):
  name = db.StringField( max_length=50, required=True)
  email = db.StringField(unique=True, required=True)
  password = db.BinaryField(required=True)
  isAdmin = db.BooleanField(default=False)