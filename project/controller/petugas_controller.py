from flask import request
from flask_restx import Resource, Namespace, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt
from project.service.petugas_service import PetugasService

api = Namespace("Petugas", "Endpoint untuk petugas")
ps = PetugasService()

# mendefinisikan model untuk register kandidat
contact = {}
contact["phone"] = fields.String(attribute="phone")
contact["email"] = fields.String(attribute="email")

alamat = {}
alamat["provinsi"] = fields.String(attribute="provinsi")
alamat["kota"] = fields.String(attribute="kota")
alamat["alamat_lengkap"] = fields.String(attribute="alamat_lengkap")

register_kandiat_model = api.model(
    "Model untuk registrasi kandidat",
    {
        "nomor_urut": fields.Integer(required=True),
        "nama_kandidat": fields.String(required=True),
        "contact": fields.Nested(contact, required=True),
        "alamat": fields.Nested(alamat, required=True),
        "image_url": fields.String(required=True),
    },
)

register_pemilih_model = api.model(
    "Model untuk registrasi pemilh",
    {
        "pemilih_id":fields.String(required=True),
        "nama_lengkap": fields.String(required=True),
        "contact": fields.Nested(contact, required=True),
        "alamat":fields.Nested(alamat, required=True)
    }
)

message_object = api.model(
    "Message Object Model",
    {"status": fields.String, "message": fields.String},
)


@api.route("/register/kandidat")
class RegisterKandidat(Resource):
    @api.doc(responses={200: "OK", 500: "Internal server error"})
    @jwt_required()
    @api.expect(register_kandiat_model)
    def post(self):
        user_data = get_jwt()["sub"]
        json_data = request.json
        result = ps.RegisterKandidat(json_data, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(500, result)

@api.route("/register/pemilih")
class RegisterPemilih(Resource):
    @api.doc(responses={200: "OK", 500: "Internal server error"})
    @jwt_required()
    @api.expect(register_pemilih_model)
    def post(self):
        user_data = get_jwt()["sub"]
        json_data = request.json
        result = ps.RegisterPemilih(json_data, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(500, result)
