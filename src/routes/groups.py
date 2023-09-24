from src import app, Config
from flask import request
from flask_api import status
from src.services import groupsService, accessManageService, userService

# from src.routes import shared
from src.models import groupsModel, accessManagementModel
from src.services.security import authorization, accessCheck


@app.route("/groups", methods=["GET"])
@authorization
def getGroups(user):
    if user["isAdmin"]:
        data = groupsModel.Groups.objects()
        return {
            "success": True,
            "data": data,
        }, status.HTTP_200_OK

    data = accessManageService.findUserGroups(user["id"])

    return {
        "success": True,
        "data": data,
    }, status.HTTP_200_OK


@app.route("/groups/create", methods=["POST"])
@authorization
def createNewGroup(user):
    try:
        req = request.get_json()
        name = req["name"]
        description = req["description"]
    except KeyError:
        return {
            "success": False,
            "message": "missing fields"
        }, status.HTTP_400_BAD_REQUEST

    data = groupsModel.Groups(name=name, description=description).save()
    access = accessManagementModel.AccessManager(
        groupId=data["id"], userId=user["id"], accessLevel=accessManagementModel.AccessLevel.ADMIN).save()

    return {
        "success": True,
        "message": "Group created",
        "id": str(data["id"])
    }, status.HTTP_200_OK


@app.route("/groups/manage/updategroupinfo/<groupId>", methods=["PUT"])
@authorization
@accessCheck(accessManagementModel.AccessLevel.ADMIN)
def updateGroupInfo(user, groupId):
    try:
        req = request.get_json()
        name = req["name"]
        description = req["description"]
    except KeyError:
        return {
            "success": False,
            "message": "missing fields"
        }, status.HTTP_400_BAD_REQUEST
    
    updateData = groupsModel.Groups.objects(id=groupId).update_one(
        set__name=name, set__description=description)

    if not updateData:
        return {
            "success": False,
            "message": "Group not found",
        }, status.HTTP_400_BAD_REQUEST

    return {
        "success": True,
        "message": "Group info updated",
    }, status.HTTP_200_OK


@app.route("/groups/manage/access/<groupId>", methods=["PUT"])
@authorization
@accessCheck(accessManagementModel.AccessLevel.ADMIN)
def updateGroupAccessToUser(user, groupId):
    try:
        req = request.get_json()
        userEmail = req["userEmail"]
        role = req["role"]
    except KeyError:
        return {
            "success": False,
            "message": "missing fields"
        }, status.HTTP_400_BAD_REQUEST

    userToUpdate = userService.findUserByEmail(userEmail)
    if not userToUpdate:
        return {
            "success": False,
            "message": "user not found"
        }, status.HTTP_400_BAD_REQUEST

    accessToUpdate = accessManagementModel.AccessLevel.READ_ONLY
    if role == "admin":
        accessToUpdate = accessManagementModel.AccessLevel.ADMIN
    elif role == "write":
        accessToUpdate = accessManagementModel.AccessLevel.WRITE
    elif role == "revoke":
        accessManagementModel.AccessManager.objects(
            userId=userToUpdate["id"]).delete()
        return {
            "success": True,
            "message": "Access revoked"
        }, status.HTTP_200_OK

    update = accessManagementModel.AccessManager.objects(
        userId=userToUpdate["id"], groupId=groupId).update_one(set__accessLevel=accessToUpdate)
    if not update:
        create = accessManagementModel.AccessManager(
            groupId=groupId, userId=userToUpdate["id"], accessLevel=accessToUpdate).save()
    return {
        "success": True,
        "message": "Access updated",
    }, status.HTTP_200_OK


@app.route("/groups/search/users/<groupId>", methods=["GET"])
@authorization
@accessCheck(accessManagementModel.AccessLevel.READ_ONLY)
def searchGroupUsers(user, groupId):
    search = request.args.get("search")
    data = groupsService.searchUsersInGroup(search, groupId)

    return {
        "success": True,
        "data": data,
    }, status.HTTP_200_OK


@app.route("/groups/delete/<groupId>", methods=["DELETE"])
@authorization
@accessCheck(accessManagementModel.AccessLevel.ADMIN)
def deleteGroup(user, groupId):
    groupsService.wipeGroup(groupId)
    return {
        "success": True,
        "message": "wiped group",
    }, status.HTTP_200_OK
