from src import app, Config
from flask import request
from flask_api import status

from src.models import accessManagementModel, messagesModel
from src.services.security import authorization, accessCheck
from src.services import accessManageService, messagingServices

@app.route("/messaging/create/<groupId>", methods=["POST"])
@authorization
@accessCheck(accessManagementModel.AccessLevel.WRITE)
def createNewMessageToGroup(user, groupId):
    try:
        req = request.get_json()
        message = req["message"]
    except KeyError:
        return {
            "success": False,
            "message": "missing fields"
        }, status.HTTP_400_BAD_REQUEST

    messagesModel.Messages(
        userId=user["id"], groupId=groupId, body=message).save()
    return {
        "success": True,
        "message": "Message created",
    }, status.HTTP_200_OK


@app.route("/messaging/get/<groupId>", methods=["GET"])
@authorization
@accessCheck(accessManagementModel.AccessLevel.READ_ONLY)
def getMessagesOfGroup(user, groupId):
    data = messagingServices.getGroupMessagesWithSenderInfo(groupId)
    return {
        "success": True,
        "data": data,
    }, status.HTTP_200_OK

@app.route("/messaging/togglelike/<groupId>/<messageId>", methods=["POST"])
@authorization
@accessCheck(accessManagementModel.AccessLevel.READ_ONLY)
def toggleLike(user, groupId, messageId):
    data = messagingServices.toggleLike(messageId,groupId, user["id"])
    return {
        "success": True,
        "data": "reacted",
    }, status.HTTP_200_OK