from src.models import usersModel
from flask_mongoengine import mongoengine
from flask_api import status 
import bcrypt

def findUserByEmail(email):
    return usersModel.User.objects(email=email).first()

def createUser(name, email, password, isAdmin):
    password = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())
    try:
        data = usersModel.User(name=name, email=email,
                        password=password, isAdmin=isAdmin).save()
    except mongoengine.errors.NotUniqueError as e:
        return {
            "success": False,
            "message": "User exists"
        }, status.HTTP_400_BAD_REQUEST
    except mongoengine.errors.ValidationError as e:
        return {
            "success": False,
            "message": str(e)
        }, status.HTTP_400_BAD_REQUEST
    except Exception as e:
        print("Unknown error", e)
        return {
            "success": False,
            "message": "Unknown error occurred"
        }, status.HTTP_400_BAD_REQUEST
