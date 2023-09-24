from flask import Flask
from config import Config, TestConfig
from flask_mongoengine import MongoEngine
import sys
from mongoengine.connection import disconnect
import mongoengine
from flask_api import status

app = Flask(__name__)
app.config.from_object(Config)

db = MongoEngine()
db.init_app(app)


def test_app():
    disconnect()
    app = Flask(__name__)
    app.config.from_object(TestConfig)
    db = MongoEngine()
    db.init_app(app)

from src.routes import messaging
from src.routes import users
from src.routes import groups