from blog.apps import db
from datetime import datetime


class Comment(db.Model):
    __tablename__ = 'comments'
    # 包含评论id,评论内容,文章作者id,评论的作者用户id,创建时间,修改时间
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(255))
    article_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255))
    createdAt = db.Column(db.DateTime, nullable=False)


class Tag(db.Model):
    __tablename__ = 'tags'
    # 文章标签id和标签内容
    id = db.Column(db.Integer, nullable=False, autoincrement=True, primary_key=True)
    articleId = db.Column(db.String(255))
    name = db.Column(db.String(255), nullable=False)
