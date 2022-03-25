from datetime import datetime
from blog.apps import db

'''
文章
'''


class Article(db.Model):
    __tablename__ = 'articles'
    # 包含id,用户id,文章标识,标题,描述,文章主体,创建时间,更改时间
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255))
    slug = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))
    body = db.Column(db.String(255))
    createdAt = db.Column(db.DateTime, nullable=False)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.now)


class ArticleFavorite(db.Model):
    __tablename__ = 'article_favorites'
    # 包含文章id和用户id
    articleId = db.Column(db.String(255), nullable=False, primary_key=True)
    userId = db.Column(db.String(255), nullable=False, primary_key=True)


class Follow(db.Model):
    # 用户id和跟随的作者id
    __tablename__ = 'followsss'
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    userid = db.Column(db.String(255), nullable=False, default='0')
    followid = db.Column(db.String(255), nullable=False, default='0')
