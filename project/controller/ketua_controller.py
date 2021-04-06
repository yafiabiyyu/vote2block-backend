from flask import request, jsonify
from flask_restx import Resource, Namespace, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt
from project.service.ketua_service import KetuaService
from project.service.user_info_service import UserInfo


api = Namespace(
    "Ketua Penyelenggara",
    "Endpoint untuk Ketua Penyelenggara"
)
ks = KetuaService()
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



user_data_model = api.model("Ketua Data", {
    'nama_lengkap':fields.String,
    'username':fields.String,
    'contact':fields.Nested(contact),
    'alamat':fields.Nested(alamat),
    'access':fields.Nested(access),
    'ethereum':fields.Nested(ethereum)
})

@api.route('/info')
class KetuaInfo(Resource):
    @jwt_required()
    @marshal_with(user_data_model, envelope="data")
    def get(self):
        try:
            user_data = get_jwt()['sub']
            result = us.GetUserInfo(user_data)
            return result
        except Exception as e:
            api.abort(400, e)

@api.route("/manage/admin")
class ManageAdmin(Resource):
    @jwt_required()
    def post(self):
        user_data = get_jwt()['sub']
        json_data = request.json
        result = ks.AddAdminPetugas(json_data, user_data)
        if result['status'] == "Berhasil" or result['status'] == "Gagal":
            return result
        else:
            api.abort(400, result['message'])