import config
import boto3

from flask import Flask
from flask_cors import CORS

from model import UserDAO, TagDAO, ImageDAO
from model.models import db
from service import UserService, ImageService, TagService
from view import create_endpoints


class Services:
    pass


################################
# Create App
################################
def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    app.config['CORS_HEADERS'] = 'Content-Type'

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.app_context().push()

    ## Persistenace Layer
    user_dao = UserDAO(db)
    tag_dao = TagDAO(db)
    image_dao = ImageDAO(db)

    ## Business Layer
    s3_client = boto3.client(
        "s3",
        aws_access_key_id     = app.config['S3_ACCESS_KEY'],
        aws_secret_access_key = app.config['S3_SECRET_KEY']
    )

    tensor_server_url = app.config['TENSOR_URL']

    services = Services
    services.user_service = UserService(user_dao, app.config)
    services.tag_service = TagService(tag_dao)
    services.image_service = ImageService(image_dao, app.config, s3_client, tensor_server_url)


    ## 엔드포인트들을 생성
    create_endpoints(app, services)

    return app

