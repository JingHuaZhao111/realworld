import datetime
import json
from blog.apps import db
from blog.apps.Comment import comment_blue
from blog.apps.Comment.comment_model import Tag, Comment
from flask import request, session
from blog.apps.User.user_model import User
from blog.apps.Article.article_model import Follow
from blog.apps.Article.article_model import Article, ArticleFavorite


@comment_blue.route('/api/tags', methods=('GET',))
def GetTags():
    tagList = Tag.query.filter().all()
    List = []
    for i in tagList:
        List.append(i.name)
    data = {'tags': List}
    return data


@comment_blue.route('/api/articles/<slug>/comments', methods=('POST',))
def AddComment(slug):
    if 'id' in session:
        data = request.get_json()
        body = data.get('comment').get('body')
        article = Article.query.filter(Article.slug == slug).first()
        author = User.query.filter(User.id == session.get('id')).first()
        articleAuthor = User.query.filter(User.id == article.user_id).first()
        following = False
        if Follow.query.filter(Follow.followid == session.get('id'), Follow.userid == articleAuthor.id).first():
            following = True
        authorJson = {"username": author.username, "bio": author.bio, "image": author.image, "following": following}
        id = len(Comment.query.filter(Comment.article_id == article.id).all()) + 1
        createdAt = datetime.datetime.now()
        comment = Comment(id=id, body=body, article_id=article.id, user_id=author.id, createdAt=createdAt)
        db.session.add(comment)
        db.session.commit()
        data = {"comment": {"id": id, "createdAt": createdAt, "body": body, "author": authorJson}}
        return data
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401


@comment_blue.route('/api/articles/<slug>/comments', methods=("GET",))
def GetComments(slug):
    article = Article.query.filter(Article.slug == slug).first()
    comments = Comment.query.filter(Comment.article_id == article.id).all()
    commentsList = []
    if not comments:
        pass
    else:
        for i in comments:
            user = User.query.filter(User.id == i.user_id).first()
            following = False
            if session.get('id'):
                if Follow.query.filter(Follow.followid == session.get('id'), Follow.userid == user.id).first():
                    following = True
            author = {"username": user.username, "bio": user.bio, "image": user.image, "following": following}
            comment = {"id": i.id, "createdAt": i.createdAt, "body": i.body, "author": author}
            commentsList.append(comment)
    return {"comments": commentsList}


@comment_blue.route('/api/articles/<slug>/comments/<id>', methods=('DELETE',))
def DeleteComment(slug, id):
    if session.get('id'):
        userId = session.get('id')
        article = Article.query.filter(Article.slug == slug).first()
        following = False
        if Comment.query.filter(Comment.id == id, Comment.article_id == article.id):
            if not Comment.query.filter(Comment.user_id==userId).first():
                return {
                    "errors": {
                        "body": [
                            "can't access"
                        ]
                    }
                }, 401
            comment = Comment.query.filter(Comment.id == id, Comment.article_id == article.id).first()
            user = User.query.filter(User.id == comment.user_id).first()
            if Follow.query.filter(Follow.followid == session.get('id'), Follow.userid == user.id).first():
                following = True
            author = {"username": user.username, "bio": user.bio, "image": user.image, "following": following}
            commentJson = {"id": comment.id, "createdAt": comment.createdAt, "body": comment.body, "author": author}
            db.session.delete(comment)
            db.session.commit()
            comments = Comment.query.filter(Comment.id > id, Comment.article_id == article.id).all()
            for i in comments:
                i.id = i.id - 1
                db.session.add(i)
            db.session.commit()
            return commentJson

        else:
            return {
                       "errors": {
                           "body": [
                               "comment's id don't exist"
                           ]
                       }
                   }, 404
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401
