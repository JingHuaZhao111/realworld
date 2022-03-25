import datetime
import json
import uuid

from flask import request, session, make_response, jsonify

from blog.apps.Article import article_blue

from blog.apps import db
from blog.apps.User.user_model import User
from blog.apps.Article.article_model import Article, ArticleFavorite, Follow
from blog.apps.Comment.comment_model import Tag

from blog.config import ComplexEncoder


def SlugGet(slug):
    article = Article.query.filter(Article.slug == slug).first()
    author_id = article.user_id
    author_information = User.query.filter(User.id == author_id).first()
    if session.get('id'):
        following = False
        if Follow.query.filter(Follow.followid == session.get('id'),
                               Follow.userid == author_id).first():
            following = True
        author = ({"bio": author_information.bio,
                   "following": following,
                   "image": author_information.image,
                   "username": author_information.username
                   })
        favorited = False
        if ArticleFavorite.query.filter(ArticleFavorite.articleId == article.id,
                                        ArticleFavorite.userId == session.get('id')).first():
            favorited = True
        favorited = favorited
    else:
        author = ({"bio": author_information.bio, "following": False,
                   "image": author_information.image,
                   "username": author_information.username
                   })
        favorited = False
    tagList = []
    tags = Tag.query.filter(Tag.articleId == article.id).all()
    for i in tags:
        tagList.append(i.name)
    body = article.body
    createdAt = article.createdAt
    updateAt = article.updatedAt
    title = article.title
    description = article.description
    fcount = ArticleFavorite.query.filter(ArticleFavorite.articleId == article.id).count()
    data = {'author': author, 'body': body, 'createdAt': createdAt, 'updateAt': updateAt,
            'description': description, 'favorited': favorited, 'favoritesCount': fcount,
            'title': title, 'tagList': tagList}
    return data


@article_blue.route('/api/profiles/<username>', methods=('GET',))
def GetProfile(username):
    try:
        user = User.query.filter(User.username == username).first()
        if session.get('id'):
            if Follow.query.filter(Follow.userid == session.get('id')).first():
                data = ({"profile": {"email": user.email,
                                     "username": user.username, "bio": user.bio,
                                     "image": user.image, "following": True}})
                return data
        data = ({"profile": {"email": user.email,
                             "username": user.username, "bio": user.bio,
                             "image": user.image, "following": False}})
        return data
    except Exception:
        return {
                   "errors": {
                       "body": [
                           "user don't exist"
                       ]
                   }
               }, 603


@article_blue.route('/api/profiles/<username>/follow', methods=('POST',))
def FollowUser(username):
    if 'id' in session:
        if User.query.filter(User.username == username).first():
            user = User.query.filter(User.username == username).first()
            if user.id==session.get('id'):
                return {"errors": {
                "body": [
                    "you can't follow yourself"
                ]
            }
                       },604
            if not Follow.query.filter(Follow.followid == session.get('id'),Follow.userid==user.id).first():
                follow = Follow()
                follow.userid = user.id
                follow.followid = session.get('id')
                db.session.add(follow)
                db.session.commit()
            return {"profile": {"email": user.email,
                                "username": user.username, "bio": user.bio,
                                "image": user.image, "following": True}}
        else:
            return {"errors": {
                "body": [
                    "username don't exist"
                ]
            }},603
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401


@article_blue.route('/api/profiles/<username>/follow', methods=('DELETE',))
def UnfollowUser(username):
    if not User.query.filter(User.username == username).first():
        return {"errors": {
                "body": [
                    "username don't exist"
                ]
            }},603
    if session.get('id'):
        user = User.query.filter(User.username == username).first()
        #未关注的也直接返回相同json
        if Follow.query.filter(Follow.followid == session.get('id')).first():
            follow=Follow.query.filter(Follow.followid == session.get('id')).first()
            db.session.delete(follow)
            db.session.commit()
        return ({"profile": {"email": user.email,
                             "username": user.username, "bio": user.bio,
                             "image": user.image, "following": False}})
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401


@article_blue.route('/api/articles', methods=('POST',))
def CreateArticle():
    if 'id' in session:
        data = request.get_json()
        article = data.get("article")
        user = User.query.filter(User.id == session.get('id')).first()
        # 创作者自己不能关注自己,数据库中体现为userid不是followid
        author = {"username": user.username, "bio": user.bio, "image": user.image, "following": False}
        createdAt = datetime.datetime.now()
        updateAt = datetime.datetime.now()
        favorited = False
        favoritesCount = 0
        title = article.get("title")
        description = article.get("description")
        body = article.get("body")
        tagList = article.get("tagList")
        articleId = str(uuid.uuid4())
        if not description or not body or not title:
            return {"errors": {
            "body": [
                "please enter title and body and description"
            ]
        }
        },601
        slug = title.replace(' ', '-')
        if tagList:
            for i in tagList:
                if not Tag.query.filter(Tag.name == i).first():
                    tag = Tag(articleId=articleId, name=i)
                    db.session.add(tag)
        articleCreate = Article(id=articleId, title=title, description=description,
                                body=body, user_id=user.id,
                                slug=slug, createdAt=createdAt, updatedAt=updateAt)

        db.session.add(articleCreate)
        db.session.commit()
        article.update({"createAt": createdAt, "updateAt": updateAt,
                        "favorited": favorited, "favoritesCount": favoritesCount,
                        "author": author})
        data = {"article": article}
        return data
    else:
        return {
                   "errors": {
                       "body": [
                           "please login"
                       ]
                   }
               }, 401


@article_blue.route('/api/articles/<slug>', methods=('GET',))
def GetArticle(slug):
    try:
        data = SlugGet(slug)
        data = {"article": data}
        data = json.dumps(data, cls=ComplexEncoder)
        return data
    except Exception:
        return {
                   "errors": {
                       "body": [
                           "no article"
                       ]
                   }
               }, 404


@article_blue.route('/api/articles/feed', methods=('GET',))
def FeedArticles():
    if session.get('id'):
        List = Follow.query.filter(Follow.followid == session.get('id')).all()

        datas = {}
        if not List:
            datas = {"article": []}
        else:
            newList = []
            articlesCount = 0
            for i in List:
                articles = Article.query.filter(Article.user_id == i.userid).all()
                for article in articles:
                    newList.append(SlugGet(article.slug))
                articlesCount = articlesCount + len(articles)
            datas = {"article": newList, "articlesCount": articlesCount}
        return datas
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401


@article_blue.route('/api/articles', methods=("GET",))
def ListArticles():
    # 只能单个筛选,T^T
    # User.query.filter(age=18).offset(2).limit(3)   跳过二条开始查询，限制输出3条
    limit = 20
    offset = 0
    articleList = Article.query.filter().order_by(Article.updatedAt).offset(offset).limit(limit).all()
    if request.args.get('limit'):
        limit = request.args.get('limit')
        articleList = Article.query.filter().order_by(Article.updatedAt).offset(offset).limit(limit).all()
    if request.args.get('offset'):
        offset = request.args.get('offset')
        articleList = Article.query.filter().order_by(Article.updatedAt).offset(offset).limit(limit).all()
    if request.args.get('author'):
        author = request.args.get('author')
        user = User.query.filter(User.username == author).first()
        articleList = Article.query.filter(Article.user_id == user.id).order_by(Article.updatedAt).offset(offset).limit(
            limit).all()
    if request.args.get('tag'):
        tag = request.args.get('tag')
        tagList = Tag.query.filter(Tag.name == tag).all()
        articleList=[]
        if not tagList:
            return {}
        for i in tagList:
            article = Article.query.filter(Article.id == i.articleId).order_by(Article.updatedAt).offset(offset).limit(
                limit).first()
            articleList.append(article)
    if request.args.get('favorited'):
        if 'id' in session:
            favorited = request.args.get('favorited')
            if ArticleFavorite.query.filter(ArticleFavorite.userId == session.get('id')).all():
                articleList = ArticleFavorite.query.filter(ArticleFavorite.userId == session.get('id')).all()
            else:
                articleList = Article.query.filter().order_by(Article.updatedAt).offset(offset).limit(limit).all()
        else:
            articleList = Article.query.filter().order_by(Article.updatedAt).offset(offset).limit(limit).all()
    datas = []
    for i in articleList:
        datas.append(SlugGet(i.slug))
    articlesCount = len(datas)
    return {"articles": datas, "articlesCount": articlesCount}


@article_blue.route('/api/articles/<slug>', methods=("PUT",))
def UpdateArticle(slug):
    data = request.get_json()
    data = data.get('article')
    if session.get('id'):
        if Article.query.filter(Article.slug == slug).first():
            if not Article.query.filter(Article.slug == slug).first().user_id==session.get('id'):
                return {
                    "errors": {
                        "body": [
                            "can't access"
                        ]
                    }
                }, 401
            article = Article.query.filter(Article.slug == slug).first()
            if data.get('title'):
                article.title = data.get('title')
                article.slug = data.get('title').replace(' ', '-')
            if data.get('description'):
                article.description = data.get('description')
            if data.get('body'):
                article.body = data.get('body')
            article.updatedAt = datetime.datetime.now()
            db.session.add(article)
            db.session.commit()
            data = {"article": SlugGet(article.slug)}
            return data
        else:
            return {
                       "errors": {
                           "body": [
                               "article don't exist"
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


@article_blue.route('/api/articles/<slug>', methods=('DELETE',))
def DeleteArticle(slug):
    if session.get('id'):
        if Article.query.filter(Article.slug == slug).first():
            if not Article.query.filter(Article.slug == slug).first().user_id==session.get('id'):
                return {
                    "errors": {
                        "body": [
                            "can't access"
                        ]
                    }
                }, 401

            data = SlugGet(slug)
            article = Article.query.filter(Article.slug == slug).first()
            #不仅删除文章,还要删除对应的标签关系
            tagList=Tag.query.filter(Tag.articleId==article.id).all()
            for i in tagList:
                db.session.delete(i)
            db.session.delete(article)
            db.session.commit()
            return data
        else:
            return {
                       "errors": {
                           "body": [
                               "article don't exist"
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


@article_blue.route('/api/articles/<slug>/favorite', methods=('POST',))
def FavoriteArticle(slug):
    if session.get('id'):
        article = Article.query.filter(Article.slug == slug).first()
        article_id = article.id
        if not ArticleFavorite.query.filter(ArticleFavorite.articleId == article_id,
                                            ArticleFavorite.userId == session.get('id')).first():
            articleFavorite = ArticleFavorite(articleId=article_id, userId=session.get('id'))
            db.session.add(articleFavorite)
            db.session.commit()
            data = {'article': SlugGet(slug)}
            return data
        else:
            data = {'article': SlugGet(slug)}
            return data
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401


@article_blue.route('/api/articles/<slug>/favorite', methods=('DELETE',))
def UnFavoritedArticle(slug):
    if session.get('id'):
        article = Article.query.filter(Article.slug == slug).first()
        article_id = article.id
        if ArticleFavorite.query.filter(ArticleFavorite.articleId == article_id,
                                        ArticleFavorite.userId == session.get('id')).first():
            articleFavorite = ArticleFavorite.query.filter(ArticleFavorite.articleId == article_id,
                                                           ArticleFavorite.userId == session.get('id')).first()
            db.session.delete(articleFavorite)
            db.session.commit()
        data = {"article": SlugGet(slug)}
        return data
    else:
        return {
                   "errors": {
                       "body": [
                           "can't access"
                       ]
                   }
               }, 401
