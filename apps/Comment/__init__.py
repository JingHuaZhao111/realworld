from flask import Blueprint
comment_blue = Blueprint('comment', __name__, url_prefix='/')
from blog.apps.Comment import views
