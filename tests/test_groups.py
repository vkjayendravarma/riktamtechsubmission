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

@pytest.fixture
def client_groups():
    with app.app_context():
        test_app()
        client = app.test_client()
        yield client

@pytest.fixture(autouse=True,scope="session")
def setup_groups_teardown():
    with app.app_context():
        yield
        connection = MongoClient(TestConfig.MONGODB_SETTINGS["host"])
        connection.drop_database(TestConfig.MONGODB_SETTINGS["db"])     

def test_setup_groups(client_groups):
    userService.createUser(consts.admin["name"], consts.admin["email"], consts.admin["password"], consts.admin["isAdmin"])

    userService.createUser(consts.user1["name"], consts.user1["email"], consts.user1["password"], consts.user1["isAdmin"])

    userService.createUser(consts.user2["name"], consts.user2["email"], consts.user2["password"], consts.user2["isAdmin"])

    userService.createUser(consts.user3["name"], consts.user3["email"], consts.user3["password"], consts.user3["isAdmin"])

    userService.createUser(consts.user4["name"], consts.user4["email"], consts.user4["password"], consts.user4["isAdmin"])

    response = client_groups.post("/login", json=consts.admin)
    adminToken["Authorization"] = "Bearer " + response.json["token"]

    response1 = client_groups.post("/login", json=consts.user1)
    user1Token["Authorization"] = "Bearer " + response1.json["token"]

    response2 = client_groups.post("/login", json=consts.user2)
    user2Token["Authorization"] = "Bearer " + response2.json["token"]

    response3 = client_groups.post("/login", json=consts.user3)
    user3Token["Authorization"] = "Bearer " + response3.json["token"]

    response4 = client_groups.post("/login", json=consts.user4)
    user4Token["Authorization"] = "Bearer " + response4.json["token"]


def test_groups_create_new_group(client_groups):
    data = {
        "name": "Test group 1",
        "description": "Test description 1"
    }
    response = client_groups.post("/groups/create",headers=user1Token, json=data)
    groupId = response.json["id"]
    groups.append(groupId)
    assert response.status_code == 200

    response = client_groups.get("/groups",headers=user1Token)
    assert response.json["data"][0]["accessLevel"] == "admin"

def test_groups_add_access_to_users(client_groups):
    data = {
        "userEmail": consts.user2["email"],
        "role": "write"
    }
    groupId = groups[0]
    response = client_groups.put("/groups/manage/access/" + groupId,headers=user1Token, json=data)
    assert response.status_code == 200

    data = {
        "userEmail": consts.user3["email"],
        "role": "read_only"
    }
    response = client_groups.put("/groups/manage/access/" + groupId,headers=user1Token, json=data)
    assert response.status_code == 200

def test_groups_update_group_info(client_groups):
    data = {
         "name": "Test group update",
        "description": "Test description update"
    }
    groupId = groups[0]
    response = client_groups.put("/groups/manage/updategroupinfo/" + groupId,headers=user1Token, json=data)
    assert response.status_code == 200

    response = client_groups.put("/groups/manage/updategroupinfo/" + groupId,headers=user2Token, json=data)
    assert response.status_code == 400

    response = client_groups.put("/groups/manage/updategroupinfo/" + groupId,headers=user3Token, json=data)
    assert response.status_code == 400

    response = client_groups.put("/groups/manage/updategroupinfo/" + groupId,headers=user4Token, json=data)
    assert response.status_code == 400

def test_groups_get_user_groups_user_with_no_group_access(client_groups):
    groupId = groups[0]
    response = client_groups.get("/groups",headers=user4Token)
    userGroups = response.json["data"]
    assert response.status_code == 200
    assert not len(userGroups)

def test_groups_search_users(client_groups):
    groupId = groups[0]
    response = client_groups.get("/groups/search/users/" + groupId + "?search=test",headers=user1Token)
    users = response.json["data"]
    assert response.status_code == 200
    assert len(users) == 3
    response = client_groups.get("/groups/search/users/" + groupId + "?search=" + consts.user2["email"],headers=user1Token)
    users = response.json["data"]
    assert response.status_code == 200
    assert len(users) == 1