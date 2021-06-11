from flask import request
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt
from project.service.auth_service import AuthService

auth = AuthService()
api = Namespace("Auth Service", "Endpoint untuk Authentication")
auth_model = api.model(
    "Auth Model Data",
    {
        "username": fields.String(
            required=True,
            description="Username dari pengguna yang akan menggunakan aplikasi",
        ),
        "password": fields.String(
            required=True,
            description="Password dari pengguna yang akan menggunakan aplikasi",
        ),
    },
)

data_resource = {}
data_resource["access_token"] = fields.String(attribute="access_token")
data_resource["refresh_token"] = fields.String(
    attribute="refresh_token"
)

message_object = api.model(
    "Message object model",
    {
        "status": fields.String,
        "message": fields.String,
        "data": fields.Nested(data_resource, skip_none=True),
    },
)


@api.route("/admin/login")
class LoginAdmin(Resource):
    @api.doc(responses={200: "OK", 404: "User not Found"})
    @api.expect(auth_model)
    @api.marshal_with(message_object)
    def post(self):
        get_user_data = request.json
        result = auth.AdminLoginService(get_user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(404, result["message"])


@api.route("/pemilih/login")
class LoginPemilih(Resource):
    @api.doc(responses={200: "OK", 404: "User not Found"})
    @api.expect(auth_model)
    @api.marshal_with(message_object)
    def post(self):
        get_user_data = request.json
        result = auth.PemilihLoginService(get_user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(404, result["message"])


@api.route("/logout")
class LogoutResource(Resource):
    @api.doc(responses={200: "OK", 400: "Bad Requests"})
    @api.marshal_with(message_object)
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        try:
            result = auth.LogoutService(jti)
            return result
        except Exception:
            return api.abort(
                400, {"status": "gagal", "message": "terjadi kesalahan"}
            )
