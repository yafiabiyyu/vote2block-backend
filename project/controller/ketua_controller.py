from flask import request, jsonify
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt
from project.service.ketua_service import KetuaService


api = Namespace(
    "Ketua Penyelenggara",
    "Endpoint untuk Ketua Penyelenggara"
)
ks = KetuaService()


# fields untuk response get petugas
contact_fields = {}
contact_fields['phone'] = fields.String(attribute="phone")
contact_fields['email'] = fields.String(attribute="email")

alamat_fields = {}
alamat_fields['provinsi'] = fields.String(attribute="provinsi")
alamat_fields['kota'] = fields.String(attribute="kota")
alamat_fields['alamat_lengkap'] = fields.String(attribute="alamat_lengkap")

access_fields = {}
access_fields['level'] = fields.Integer(attribute="level")
access_fields['group'] = fields.String(attribute="group")

main_fields = {}
main_fields['username'] = fields.String
main_fields['nama_lengkap'] = fields.String
main_fields['contact'] = fields.Nested(contact_fields)
main_fields['alamat'] = fields.Nested(alamat_fields)
main_fields['access'] = fields.Nested(access_fields)

@api.route('/manage/admin')
class ManageAdminPetugas(Resource):
    @jwt_required()
    def post(self):
        try:
            ketua_address = get_jwt()['eth_wallet']
            user_data = get_jwt()['sub']
            get_json_data = request.json
            result = ks.AddAdminPetugas(get_json_data, ketua_address, user_data)
            # return jsonify(result)
        except Exception as e:
            api.abort(400, e)

