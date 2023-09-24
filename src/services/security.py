from functools import wraps
from config import Config
import jwt
from flask import request
from flask_api import status
from src.models import usersModel
from src.services import accessManageService

def authorization(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if "Authorization" in request.headers:
            token = request.headers["Authorization"][7:]
            try:
                decode = jwt.decode(token, Config.SECRET_KEY,algorithms=Config.SESSION_ALGORITHM)   
            except Exception as e:
                return {
                    "success": False,
                    "message": "invalid token"
                },status.HTTP_401_UNAUTHORIZED   
            try:
                user = usersModel.User.objects(id=str(decode["userId"])).first()   
            except Exception as e:
                print("DB error ", e)
                return {
                    "success": False,
                    "message": "Unknown error"
                },status.HTTP_500_INTERNAL_SERVER_ERROR  
            if not user:
                return {
                "success": False,
                "message": "Unauthorized"
            }, status.HTTP_401_UNAUTHORIZED      
        else:        
            return {
                "success": False,
                "message": "Unauthorized"
            }, status.HTTP_401_UNAUTHORIZED
        return func(user, *args, **kwargs)
    return decorated


def isAdminCheck(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        user = args[0]
        if not user["isAdmin"]:
            return {
                "success": False,
                "message": "Invalid access"
            }, status.HTTP_400_BAD_REQUEST        
        return func(True, *args, **kwargs)
    return decorated


def accessCheck(accessLevel):
    def decoratorAccessCheck(function):
        @wraps(function)
        def wrapperAccessCheck(*args, **kwargs):
            user=args[0]
            groupId=kwargs["groupId"]
            if not accessManageService.groupAccessCheck(user, groupId, accessLevel):
                return {
                    "success": False,
                    "message": "Invalid access"
                }, status.HTTP_400_BAD_REQUEST
            return function(*args, **kwargs)
        return wrapperAccessCheck
    return decoratorAccessCheck
