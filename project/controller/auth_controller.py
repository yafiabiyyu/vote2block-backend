from flask import request, jsonify
from flask_restx import Resource, Namespace, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt
from project.service.auth_service import AuthService

auth = AuthService()
api = Namespace("Auth", "Endpoint untuk Authentication")
auth_model = api.model(
    "Auth Model", 
    {
        "username":fields.String(
            require=True,
            description="Username dari pengguna yang akan menggunakan aplikasi"
        ),
        "password":fields.String(
            require=True,
            description="Password dari pengguna yang akan menggunakan aplikasi"
        )
    }
)
data_resource = {}
data_resource['access_token'] = fields.String
data_resource['refresh_token'] = fields.String

message_object = api.model(
    "Message Object Model",
    {
        "status":fields.String,
        "message":fields.String,
        "data":fields.Nested(data_resource,skip_none=True)
    }
)

@api.route("/login")
class LoginResource(Resource):
    @api.doc(responses={200:"OK", 404:"User not found"})
    @api.expect(auth_model)
    @api.marshal_with(message_object)
    def post(self):
        user_data = request.json
        result = auth.LoginService(user_data)
        if result['status'] == "Berhasil" or result['status'] == "Gagal":
            return result
        else:
            api.abort(404, result)
