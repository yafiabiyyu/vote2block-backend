from flask import Blueprint
from flask_restx import Api

# Import Namespace
from .auth_controller import api as auth_ns
from .admin_controller import api as admin_ns
from .pemilih_controller import api as pemilih_ns
from .voting_controller import api as voting_ns

# from .voting_controller import api as voting_ns
controller = Blueprint("api", __name__)
api = Api(controller, version="1.0", title="Vote2Block API")
api.add_namespace(auth_ns, path="/auth")
api.add_namespace(admin_ns, path="/admin")
api.add_namespace(pemilih_ns, path="/pemilih")
api.add_namespace(voting_ns, path="/voting")
