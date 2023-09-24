from src.services import userService
from flask import Flask
from src import test_app, app, db
import pytest
from pymongo import MongoClient
import uuid
from tests import consts
from config import TestConfig

adminToken = {
    "Authorization": "",
    "Content-Type": "application/json", 
}

@pytest.fixture
def client():
    with app.app_context():
        test_app()
        client = app.test_client()
        yield client

@pytest.fixture(autouse=True,scope="session")
def setup_teardown():
    with app.app_context():
        yield
        connection = MongoClient(TestConfig.MONGODB_SETTINGS["host"])
        connection.drop_database(TestConfig.MONGODB_SETTINGS["db"])        

def test_create_admin(client):
    res = userService.createUser(consts.admin["name"], consts.admin["email"], consts.admin["password"], True)

def test_admin_login(client):
    response = client.post("/login", json=consts.admin)
    adminToken["Authorization"] = "Bearer " + response.json["token"]
    assert response.status_code == 200
    assert response.json["isAdmin"]

def test_create_normal_user(client):
    response = client.post("/users/register",headers=adminToken, json=consts.user1)
    assert response.status_code == 200

def test_create_same_normal_user(client):
    response = client.post("/users/register",headers=adminToken, json=consts.user1)
    assert response.status_code == 400