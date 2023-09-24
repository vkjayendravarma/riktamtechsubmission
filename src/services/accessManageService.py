from src.models import accessManagementModel


def groupAccessCheck(user, groupId, accessLevel):
    if user["isAdmin"]:
        return True
    data = accessManagementModel.AccessManager.objects(
        groupId=groupId, userId=user["id"]).first()
    if not data:
        return False
    if accessLevel is accessManagementModel.AccessLevel.READ_ONLY and data:
        return True
    elif accessLevel is accessManagementModel.AccessLevel.WRITE:
        return data["accessLevel"] is not accessManagementModel.AccessLevel.READ_ONLY
    elif accessLevel is accessManagementModel.AccessLevel.ADMIN:
        return data["accessLevel"] is  accessManagementModel.AccessLevel.ADMIN

    return False

def findUserGroups(userId):
    pipeline = [
        {
            "$match": {
                "userId": userId
            }
        }, {
            "$lookup": {
                "from": "groups",
                "localField": "groupId",
                "foreignField": "_id",
                "as": "group"
            }
        }, {
            "$unwind": "$group"
        }, {
            "$project": {
                "group._id": 0,
                "userId": 0,
                "_id": 0
            }
        }
    ]
    cursor = accessManagementModel.AccessManager.objects.aggregate(pipeline)
    data = []
    for doc in cursor:
        doc["groupId"] = str(doc["groupId"])
        data.append(doc)

    return data