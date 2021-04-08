from flask import request, jsonify
from flask_restx import Resource, Namespace, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt
from project.service.user_info_service import UserInfo

api = Namespace(
    "User Info",
    "Endpoint untuk mengambil data user"
)

us = UserInfo()

# nested fields list
contact = {}
contact['phone'] = fields.String(attribute='phone')
contact['email'] = fields.String(attribute='email')

alamat = {}
alamat['provinsi'] = fields.String(attribute='provinsi')
alamat['kota'] = fields.String(attribute='kota')
alamat['alamat_lengkap'] = fields.String(attribute='alamat_lengkap')

access = {}
access['level'] = fields.String(attribute='level')
access['group'] = fields.String(attribute='group')

ethereum = {}
ethereum['ethereum_address'] = fields.String(attribute='ethereum_address')
ethereum['ethereum_access'] = fields.String(attribute='ethereum_access')



user_data_model = api.model("User Data", {
    'nama_lengkap':fields.String,
    'username':fields.String,
    'contact':fields.Nested(contact),
    'alamat':fields.Nested(alamat),
    'access':fields.Nested(access),
    'ethereum':fields.Nested(ethereum)
})

user_history_model = api.model("History Data", {
    "tx_hash": fields.String(attribute="tx_hash"),
    "signature":fields.String(attribute="signature_data")
})

@api.route('/info')
class GetUserInfo(Resource):
    @jwt_required()
    @marshal_with(user_data_model, envelope="data")
    def get(self):
        try:
            user_data = get_jwt()['sub']
            result = us.GetUserInfo(user_data)
            return result
        except Exception as e:
            api.abort(400, 3)

@api.route('/riwayat')
class GetUserTxHistory(Resource):
    @jwt_required()
    @marshal_with(user_history_model, envelope="data")
    def get(self):
        user_data = get_jwt()['sub']
        result = us.GetUserHistoryTx(user_data)
        return result