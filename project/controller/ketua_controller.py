from flask import request, jsonify
from flask_restx import Resource, Namespace, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt
from project.service.ketua_service import KetuaService



api = Namespace(
    "Ketua Penyelenggara",
    "Endpoint untuk Ketua Penyelenggara"
)
ks = KetuaService()

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