from flask import Blueprint
from flask_restx import Api

# Import Namespace
from .auth_controller import api as auth_ns

controller = Blueprint("api", __name__)
api = Api(controller, version="1.0", title="Vote2Block API")
api.add_namespace(auth_ns, path="/auth")