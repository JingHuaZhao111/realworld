from blog.apps import db

'''
用户表
'''


class User(db.Model):
    __tablename__ = 'users'
    # 包含用户id,用户名,密码,邮箱,自我介绍,头像图片网址
    id = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.String(255), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    bio = db.Column(db.String(255), default=None)
    image = db.Column(db.String(511), default=None)
