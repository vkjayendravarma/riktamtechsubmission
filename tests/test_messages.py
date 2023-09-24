from src.services import userService
from flask import Flask
from src import test_app, app, db
import pytest
from pymongo import MongoClient
import uuid
import time
from tests import consts

adminToken = {
    "Authorization": "",
    "Content-Type": "application/json"
}
user1Token = {
    "Authorization": "",
    "Content-Type": "application/json"
}
user2Token = {
    "Authorization": "",
    "Content-Type": "application/json"
}
user3Token = {
    "Authorization": "",
    "Content-Type": "application/json"
}
user4Token = {
    "Authorization": "",
    "Content-Type": "application/json"
}

groups = []
groupMessages = []

@pytest.fixture
def client_messages():
    with app.app_context():
        test_app()
        client = app.test_client()
        yield client

@pytest.fixture(autouse=True,scope="session")
def setup_groups_teardown():
    with app.app_context():
        yield
        connection = MongoClient("mongodb://localhost:27017")
        connection.drop_database("test")     

def test_setup_messages(client_messages):
    userService.createUser(consts.admin["name"], consts.admin["email"], consts.admin["password"], consts.admin["isAdmin"])

    userService.createUser(consts.user1["name"], consts.user1["email"], consts.user1["password"], consts.user1["isAdmin"])

    userService.createUser(consts.user2["name"], consts.user2["email"], consts.user2["password"], consts.user2["isAdmin"])

    userService.createUser(consts.user3["name"], consts.user3["email"], consts.user3["password"], consts.user3["isAdmin"])

    userService.createUser(consts.user4["name"], consts.user4["email"], consts.user4["password"], consts.user4["isAdmin"])

    response = client_messages.post("/login", json=consts.admin)
    adminToken["Authorization"] = "Bearer " + response.json["token"]

    response1 = client_messages.post("/login", json=consts.user1)
    user1Token["Authorization"] = "Bearer " + response1.json["token"]

    response2 = client_messages.post("/login", json=consts.user2)
    user2Token["Authorization"] = "Bearer " + response2.json["token"]

    response3 = client_messages.post("/login", json=consts.user3)
    user3Token["Authorization"] = "Bearer " + response3.json["token"]

    response4 = client_messages.post("/login", json=consts.user4)
    user4Token["Authorization"] = "Bearer " + response4.json["token"]

    data = {
        "name": "Test group 1",
        "description": "Test description 1"
    }
    response = client_messages.post("/groups/create",headers=user1Token, json=data)
    groupId = response.json["id"]
    groups.append(groupId)

    data = {
        "userEmail": consts.user2["email"],
        "role": "write"
    }
    groupId = groups[0]
    response = client_messages.put("/groups/manage/access/" + groupId,headers=user1Token, json=data)

    data = {
        "userEmail": consts.user3["email"],
        "role": "read_only"
    }
    response = client_messages.put("/groups/manage/access/" + groupId,headers=user1Token, json=data)


def test_messages_create_message_group_admin(client_messages):
    groupId = groups[0]
    data = {
         "message": "hi"
    }
    response = client_messages.post("/messaging/create/" + groupId,headers=user1Token, json=data)
    assert response.status_code == 200

def test_messages_create_message_group_write(client_messages):
    groupId = groups[0]
    data = {
         "message": "hi"
    }
    response = client_messages.post("/messaging/create/" + groupId,headers=user2Token, json=data)
    assert response.status_code == 200

def test_messages_create_message_group_read_only(client_messages):
    groupId = groups[0]
    data = {
         "message": "hi"
    }
    response = client_messages.post("/messaging/create/" + groupId,headers=user3Token, json=data)
    assert response.status_code == 400

def test_messages_create_message_group_no_access(client_messages):
    groupId = groups[0]
    data = {
         "message": "hi"
    }
    response = client_messages.post("/messaging/create/" + groupId,headers=user4Token, json=data)
    assert response.status_code == 400

def test_messages_get_all_messages(client_messages):
    groupId = groups[0]
    data = {
         "message": "hi"
    }
    response = client_messages.get("/messaging/get/" + groupId,headers=user1Token, json=data)

    for message in  response.json["data"]:
        groupMessages.append(message)

    assert response.status_code == 200
    assert len(groupMessages) == 2

def test_messages_toggle_like(client_messages):
    groupId = groups[0]
    messageId = groupMessages[0]["_id"]

    response = client_messages.post("/messaging/togglelike/" + groupId + "/" + messageId,headers=user1Token)

    assert response.status_code == 200

    response = client_messages.get("/messaging/get/" + groupId,headers=user1Token)

    groupMessagesAfterLike = response.json["data"]

    assert groupMessagesAfterLike[0]["likes"] == 1

    response = client_messages.post("/messaging/togglelike/" + groupId + "/" + messageId,headers=user1Token)

    assert response.status_code == 200

    response = client_messages.get("/messaging/get/" + groupId,headers=user1Token)

    groupMessagesAfterRemovedLike = response.json["data"]

    assert groupMessagesAfterRemovedLike[0]["likes"] == 0