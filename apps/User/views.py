import uuid

from flask import request, session
from blog.apps.User import user_blue
from blog.apps.User.user_model import User
from blog.apps import db


@user_blue.route('/api/users', methods=('POST',))
def Registration():
    data = request.get_json()
    newdata = data.get("user")
    username = newdata.get("username")
    email = newdata.get("email")
    password = newdata.get("password")
    id = str(uuid.uuid4())
    if (username == None or email == None or password == None):
        return {
                   "errors": {
                       "body": [
                           "can't be empty"
                       ]
                   }
               }, 601
    if User.query.filter(User.username==username):
        return {
               "errors": {
                   "body": [
                       "username exist"
                   ]
               }
           }, 602
    if User.query.filter(User.email==email):
        return {
               "errors": {
                   "body": [
                       "email exist"
                   ]
               }
           }, 602
    user = User(id=id, username=username, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    data.update({"user": {"email": user.email,
                          "username": user.username, "bio": user.bio, "image": user.image}})

    return data


@user_blue.route('/api/users/login', methods=('POST',))
def Authentication():
    data = request.get_json()
    data = data.get("user")
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return {"errors": {
            "body": [
                "please enter email and password"
            ]
        }
        },601
    if (User.query.filter(User.password == password, User.email == email).first()):
        user = User.query.filter(User.password == password, User.email == email).first()
        data = ({"user": {"email": user.email, "username": user.username, "bio": user.bio, "image": user.image}})
        session['id'] = user.id
        return data
    else:
        return {"errors": {
            "body": [
                "username or password error"
            ]
        }
               }, 603

@user_blue.route('/api/users/logoff',methods=('GET',))
def Logoff():
    if 'id' in session:
        session.pop('id');
        return {"user":"log off successful"}
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401
@user_blue.route('/api/user', methods=('GET',))
def GetCurrentUser():
    if 'id' in session:
        user = User.query.filter(User.id == session.get('id')).first()
        data = ({"user": {"email": user.email,
                          "username": user.username, "bio": user.bio,
                          "image": user.image}})
        return data
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401


@user_blue.route('/api/user', methods=('PUT',))
def UpdateUser():
    data = request.get_json()
    data = data.get("user")
    if 'id' in session:
        user = User.query.filter(User.id == session.get('id')).first()
        if data.get("email"):
            user.email = data.get("email")
        if data.get("username"):
            user.username = data.get("username")
        if data.get("password"):
            user.password = data.get("password")
        if data.get("bio"):
            user.bio = data.get("bio")
        if data.get("image"):
            user.image = data.get("image")
        db.session.add(user)
        db.session.commit()
        data = ({"user": {"email": user.email,
                          "username": user.username, "bio": user.bio,
                          "image": user.image}})
        return data
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401
