from src.models import messagesModel, messagesLikeModel
from bson import ObjectId


def getGroupMessagesWithSenderInfo(groupId):
    pipeline = [
        {
            "$match": {
                "groupId": ObjectId(groupId)
            }
        },
        {
            "$lookup": {
                "from": "message_likes",
                "localField": "_id",
                "foreignField": "messageId",
                "as": "allLikes"
            }
        },
        {
            "$lookup": {
                "from": "user",
                "localField": "userId",
                "foreignField": "_id",
                "as": "user"
            }
        }, {
            "$unwind": "$user"
        },
        {
            "$addFields": {
                "likes": {"$size": "$allLikes"}
            }
        }, {
            "$project": {
                "groupId": 0,
                "user._id": 0,
                "user.password": 0,
                "user.isAdmin": 0,
                "allLikes": 0
            }
        }
    ]

    cursor = messagesModel.Messages.objects.aggregate(pipeline)
    data = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["userId"] = str(doc["userId"])
        data.append(doc)

    return data


def toggleLike(messageId, groupId, userId):
    # delete first
    delete = messagesLikeModel.MessageLikes.objects(
        messageId=messageId, userId=userId).delete()
    if not delete:
        messagesLikeModel.MessageLikes(
            messageId=messageId, groupId=groupId, userId=userId).save()
