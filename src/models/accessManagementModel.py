from src import db
from enum import Enum

class AccessLevel(Enum):
    READ_ONLY = 'read_only'
    WRITE = 'write'
    ADMIN = 'admin'

class AccessManager(db.Document):
    groupId=db.ObjectIdField(required=True)
    userId=db.ObjectIdField(required=True)
    accessLevel = db.EnumField(AccessLevel, default=AccessLevel.READ_ONLY)
    