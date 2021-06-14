from flask import request
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt
from project.service.pemilih_service import PemilihService

ps = PemilihService()
api = Namespace("Pemilih Controller", "Endpoint untuk pemilih")

contact = {}
contact["email"] = fields.String(attribute="email", readonly=True)
contact["phone"] = fields.String(attribute="phone", readonly=True)

alamat = {}
alamat["provinsi"] = fields.String(attribute="provinsi", readonly=True)
alamat["kota"] = fields.String(attribute="kota", readonly=True)
alamat["alamat_lengkap"] = fields.String(
    attribute="alamat_lengkap", readonly=True
)

pemilih_info_model = api.model(
    "Model untuk info pemilih",
    {
        "pemilih_id": fields.String,
        "nama_lengkap": fields.String,
        "tanggal_lahir": fields.String,
        "username": fields.String,
        "contact": fields.Nested(contact),
        "alamat": fields.Nested(alamat),
        "ethereum_address": fields.String,
        "hak_pilih": fields.Integer,
        "status_voting": fields.Boolean,
    },
)

update_password_model = api.model(
    "Model untuk update password pemilih",
    {
        "old_password": fields.String(required=True),
        "new_password": fields.String(required=True),
    },
)

message_object_model = api.model(
    "Model untuk message object",
    {
        "status": fields.String(readonly=True),
        "message": fields.String(readonly=True),
    },
)


@api.route("/detail")
class DetailPemilih(Resource):
    @jwt_required()
    @api.doc(responses={200: "OK", 500: "Internal Server Error"})
    @api.marshal_with(pemilih_info_model)
    def get(self):
        user_data = get_jwt()["sub"]
        result = ps.GetPemilihData(user_data)
        if result != "Error":
            return result
        else:
            api.abort(
                500,
                {
                    "status": "Error",
                    "message": "Terjadi masalah pada server",
                },
            )


@api.route("/update/password")
class UpdatePasswordPemilih(Resource):
    @jwt_required()
    @api.doc(responses={200: "OK", 400: "Bad Request"})
    @api.expect(update_password_model)
    def post(self):
        user_data = get_jwt()["sub"]
        json_data = request.json
        result = ps.PemilihUpdatePassword(json_data, user_data)
        if result["status"] == "Berhasil":
            return result
        else:
            api.abort(400, result)
