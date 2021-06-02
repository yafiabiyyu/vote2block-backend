from flask import request
from flask_restx import Resource, Namespace, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt
from project.service.user_info_service import UserInfo

us = UserInfo()
api = Namespace(
    "User Info", "Endpoint untuk mengambil data mengenai user"
)

# Fields setup untuk keseluruhan data pengguna
contact = {}
contact["phone"] = fields.String(attribute="phone")
contact["email"] = fields.String(attribute="email")

alamat = {}
alamat["provinsi"] = fields.String(attribute="provinsi")
alamat["kota"] = fields.String(attribute="kota")
alamat["alamat_lengkap"] = fields.String(attribute="alamat_lengkap")

access = {}
access["level"] = fields.String(attribute="level")
access["status"] = fields.String(attribute="status")

ethereum = {}
ethereum["ethereum_address"] = fields.String(
    attribute="ethereum_address"
)
ethereum["ethereum_access"] = fields.String(attribute="ethereum_access")

user_info_model = api.model(
    "User Info Model",
    {
        "nama_lengkap": fields.String,
        "username": fields.String,
        "contact": fields.Nested(contact),
        "alamat": fields.Nested(alamat),
        "access": fields.Nested(access),
        "ethereum": fields.Nested(ethereum),
    },
)

update_password_model = api.model(
    "User Update Password Model",
    {
        "old_password":fields.String(require=True),
        "new_password":fields.String(require=True)
    }
)

user_history_model = api.model(
    "History Data",
    {
        "tx_hash": fields.String(attribute="tx_hash"),
        "signature": fields.String(attribute="signature_data"),
    },
)

message_object = api.model(
    "Message Object Model",
    {
        "status":fields.String,
        "message":fields.String
    }
)

@api.route("/update/password")
class UpdatePassword(Resource):
    @api.doc(responses={200:"OK",400:"Bad Requests"})
    @api.expect(update_password_model)
    @api.marshal_with(message_object)
    @jwt_required()
    def post(self):
        user_data = get_jwt()['sub']
        json_data = request.json
        result = us.UpdatePassword(user_data, json_data)
        if result['status'] == "Berhasil":
            return result
        else:
            api.abort(400, result)

@api.route("/info")
class UserInfo(Resource):
    @jwt_required()
    @api.doc(responses={200:"OK", 400:"Bad Request"})
    @api.marshal_with(user_info_model, envelope="data")
    def get(self):
        user_data = get_jwt()['sub']
        result = us.GetUserInfo(user_data)
        return result

@api.route("/riwayat")
class GetUserTxHistory(Resource):
    @jwt_required()
    @api.marshal_list_with(user_history_model, envelope="data")
    def get(self):
        user_data = get_jwt()["sub"]
        result = us.GetUserHistoryTx(user_data)
        return result