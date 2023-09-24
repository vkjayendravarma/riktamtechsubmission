from src import app, Config
from flask import request
from flask_api import status
from src.models import usersModel
import bcrypt
import jwt
import datetime
from src.services.security import authorization, isAdminCheck
from bson import ObjectId
from flask_mongoengine import mongoengine
from src.services import userService

@app.route("/users/register", methods=["POST"])
@authorization
@isAdminCheck
def register(user, isAdmin):
    req = request.get_json()
    try:
        name = req["name"]
        email = req["email"]
        password = req["password"]
        isUserAdmin = req["isAdmin"]
    except KeyError as e:
        return {"success": False, "message": "one or more missing fields"}, status.HTTP_400_BAD_REQUEST
    
    
    createUser = userService.createUser(name=name, email=email,
                        password=password, isAdmin=isUserAdmin)
    if createUser:
        return createUser
    
    return {
        "success": True,
        "message": "User Created"
    }, status.HTTP_200_OK


@app.route("/login", methods=["POST"])
def login():
    req = request.get_json()
    email = req["email"]
    password = req["password"].encode("UTF-8")

    try:
        user = usersModel.User.objects(email=email).first()
    except Exception as e:
        print("DB operation failed", e)
        return {
            "success": False,
            "message": "Unknown error",
        }, status.HTTP_500_INTERNAL_SERVER_ERROR

    if (user):
        if (bcrypt.checkpw(password, user.password)):
            token = jwt.encode(payload={
                "userId": str(user["id"]),
                "isAdmin": user["isAdmin"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=Config.SESSION_TIME_OUT_IN_HOURS)
            },
                key=Config.SECRET_KEY,
                algorithm=Config.SESSION_ALGORITHM)
            return {
                "success": True,
                "token": token,
                "isAdmin": user["isAdmin"]
            }, status.HTTP_200_OK
        else:
            return {
                "success": False,
                "message": "Invalid password"
            }, status.HTTP_400_BAD_REQUEST

    else:
        return {
            "success": False,
            "message": "Invalid user"
        }, status.HTTP_400_BAD_REQUEST


@app.route("/users/namechange", methods=["PATCH"])
@authorization
def updateUserName(user):
    req = request.get_json()
    name = req["name"]
    email = user["email"]
    if user["isAdmin"]:
        email = ObjectId(req["email"])
    user = usersModel.User.objects(email=email).update_one(
        set__name=name)
    if not user:
        return {
            "success": False,
            "message": "User not found"
        }, status.HTTP_400_BAD_REQUEST
    else:
        return {
            "success": True,
            "message": "Name updated"
        }, status.HTTP_200_OK


@app.route("/users/passwordchange", methods=["PATCH"])
@authorization
def updateUserPassword(user):
    req = request.get_json()
    email = user["email"]
    try:
        password = req["password"].encode("UTF-8")
    except KeyError as e:
        return {"success": False, "message": "one or more missing fields"}, status.HTTP_400_BAD_REQUEST
    password = bcrypt.hashpw(password, bcrypt.gensalt())

    userUpdate = usersModel.User.objects(
            email=email).update_one(set__password=password)

    return {
        "success": True,
        "message": "Password updated"
    }, status.HTTP_200_OK


@app.route("/users/privilegechange", methods=["PATCH"])
@authorization
@isAdminCheck
def updateUserPrivilege(user, isAdmin):
    req = request.get_json()
    isAdmin = req["isAdmin"]
    email = req["email"]
    user = usersModel.User.objects(email=email).update_one(
        set__isAdmin=isAdmin)
    
    if not user:
        return {
            "success": False,
            "message": "User not found"
        }, status.HTTP_400_BAD_REQUEST
    else:
        return {
            "success": True,
            "message": "Privilege updated"
        }, status.HTTP_200_OK

@app.route("/healthcheck", methods=["POST"])
def healthCheck():
    return {
        "success": True,
        "message": "Api working"
        }, status.HTTP_200_OK