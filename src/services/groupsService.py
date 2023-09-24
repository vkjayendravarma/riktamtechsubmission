from src.models import accessManagementModel, messagesLikeModel, messagesModel, groupsModel
from bson import ObjectId


def searchUsersInGroup(searchKey, groupId):
    pipeline = [
        {
            "$match": {
                "groupId": ObjectId(groupId)
            }
        }, {
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
            "$project": {
                "name": "$user.name",
                "email": "$user.email",
                "userId": 1
            }
        }
    ]

    if searchKey and len(searchKey):
        pipeline.append({
            "$match": {
                "$or": [
                    {
                        "name": {"$regex": searchKey}
                    },
                    {
                        "email": {"$regex": searchKey}
                    },
                ]
            }
        })

    cursor = accessManagementModel.AccessManager.objects.aggregate(pipeline)
    data = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["userId"] = str(doc["userId"])
        data.append(doc)

    return data


def wipeGroup(groupId):

    # wipe likes
    messagesLikeModel.MessageLikes.objects(groupId=groupId).delete()

    # wipe messages
    messagesModel.Messages.objects(groupId=groupId).delete()

    #wipe access
    accessManagementModel.AccessManager.objects(groupId=groupId).delete()

    #wipe group info 
    groupsModel.Groups.objects(id=groupId).delete()