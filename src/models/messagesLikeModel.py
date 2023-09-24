from src import db

class MessageLikes(db.Document):
    messageId=db.ObjectIdField(required=True)
    userId=db.ObjectIdField(required=True)
    groupId=db.ObjectIdField(required=True)