from flask import request, jsonify
from flask_restx import Resource, Namespace, fields
from project.service.auth_service import AuthService
from flask_jwt_extended import jwt_required, get_jwt

api = Namespace("Auth", "Endpoint untuk Authentications")
auth_model = api.model(
    "Auth Model",
    {
        "username": fields.String(
            require=True,
            description="Username dari user yang akan menggunakan aplikasi",
        ),
        "password": fields.String(
            require=True,
            description="Password dari username yang akan menggunakan aplikasi",
        ),
    },
)
auth = AuthService()


@api.route("/login")
class LoginResource(Resource):
    @api.doc(responses={200: "OK", 404: "Username not found"})
    @api.expect(auth_model)
    def post(self):
        user_data = request.json
        print(user_data)
        login_status = auth.LoginService(user_data)
        return jsonify(login_status)


@api.route("/logout")
class LogoutResource(Resource):
    # @api.doc(
    #     responses={
    #         200:"OK",
    #         400:"Bad request"
    #     }
    # )
    @jwt_required()
    def post(self):
        print("hello")
        jti = get_jwt()["jti"]
        try:
            result = auth.LogoutService(jti)
            return jsonify(result)
        except Exception as e:
            return jsonify(
                {"status": "gagal", "message": "terjadi kesalahan"}
            )
