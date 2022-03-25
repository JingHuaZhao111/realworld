from flask import Flask, jsonify

from flask_sqlalchemy import SQLAlchemy

from blog.config import Config

db = SQLAlchemy()
app = Flask(__name__)


def create_app(config_class=Config):
    app.config.from_object(config_class)
    app.JSON_AS_ASCII = False
    db.init_app(app)
    from blog.apps.User import user_blue
    app.register_blueprint(user_blue)
    from blog.apps.Article import article_blue
    app.register_blueprint(article_blue)
    from blog.apps.Comment import comment_blue
    app.register_blueprint(comment_blue)
    return app
