from flask import Blueprint
article_blue = Blueprint('article', __name__, url_prefix='/')
from blog.apps.Article import views