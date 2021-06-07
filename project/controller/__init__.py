from flask import Blueprint
from flask_restx import Api

# Import Namespace
from .auth_controller import api as auth_ns
from .ketua_controller import api as ketua_ns
from .user_info_controller import api as user_ns
from .petugas_controller import api as petugas_ns

controller = Blueprint("api", __name__)
api = Api(controller, version="1.0", title="Vote2Block API")
api.add_namespace(auth_ns, path="/auth")
api.add_namespace(ketua_ns, path="/ketua")
api.add_namespace(user_ns, path="/user")
api.add_namespace(petugas_ns, path="/petugas")
