from flask import Blueprint
user_blue = Blueprint('user', __name__, url_prefix='/')
from blog.apps.User import views