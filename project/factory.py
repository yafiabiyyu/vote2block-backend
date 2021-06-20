from flask import Flask
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
from datetime import timedelta
from .celery_utils import init_celery

# deklarasi variabel
load_dotenv()
db = MongoEngine()
jwt = JWTManager()

PKG_NAME = os.path.dirname(os.path.realpath(__file__)).split("/")[-1]


def create_app(app_name=PKG_NAME, **kwargs):
    app = Flask(app_name)
    app.config['ERROR_404_HELP'] = False
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        JWT_SECRET_KEY=os.getenv("JWT_KEY"),
        JWT_BLACKLIST_ENABLED=True,
        JWT_BLACKLIST_TOKEN_CHECKS=["access", "refresh"],
        JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    )
    app.config.setdefault("JWT_TOKEN_LOCATION", ("headers",))
    app.config.setdefault("JWT_HEADER_NAME", "Authorization")
    app.config.setdefault("JWT_HEADER_TYPE", "Bearer")
    app.config["MONGODB_HOST"] = os.getenv("MONGO_DB_URI")
    if kwargs.get("celery"):
        init_celery(kwargs.get("celery"), app)

    # init app
    db.init_app(app)
    jwt.init_app(app)

    # import controller blueprint
    from .controller import controller as controller_blueprint

    # register bluprint to app
    app.register_blueprint(
        controller_blueprint, url_prefix="/vote2block/api/v1"
    )
    app.app_context().push()

    # import Models
    from project.models import user_model

    # jwt blacklist
    @jwt.token_in_blocklist_loader
    def CheckIfTokenInBlacklist(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return user_model.RevokedTokenDoc.IsJtiBlackListed(jti)

    return app
