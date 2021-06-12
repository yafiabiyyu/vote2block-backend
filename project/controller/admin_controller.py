from flask import request
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt
from project.service.admin_service import AdminService

adminservice = AdminService()
api = Namespace(
    "Admin Controller", "Endpoint untuk admin penyelenggara"
)

# field untuk contact dan alamat
contact = {}
contact["email"] = fields.String(attribute="email", required=True)
contact["phone"] = fields.String(attribute="phone", required=True)

alamat = {}
alamat["provinsi"] = fields.String(attribute="provinsi", required=True)
alamat["kota"] = fields.String(attribute="kota", required=True)
alamat["alamat_lengkap"] = fields.String(
    attribute="alamat_lengkap", required=True
)

pemilih_data_model = api.model(
    "Model untuk data pemilih",
    {
        "pemilih_id": fields.String(required=True),
        "nama_lengkap": fields.String(required=True),
        "tgl_lahir": fields.String(required=True),
        "contact": fields.Nested(contact),
        "alamat": fields.Nested(alamat),
    },
)

kandidat_data_model = api.model(
    "Model untuk data kandidat",
    {
        "kandidat_id": fields.String(required=True),
        "nomor_urut": fields.Integer(rquired=True),
        "nama_kandidat": fields.String(required=True),
        "tanggal_lahir": fields.String(required=True),
        "visi": fields.String(required=True),
        "misi": fields.String(required=True),
        "contact": fields.Nested(contact, required=True),
        "alamat": fields.Nested(alamat),
        "image_url": fields.String(required=True),
    },
)

all_pemilih_data = api.model(
    "Model untuk seluruh data pemilih",
    {
        "id": fields.String(readonly=True),
        "nama_lengkap": fields.String(readonly=True),
        "tanggal_lahir": fields.String(readonly=True),
    },
)

all_kandidat_data = api.model(
    "Model untuk seluruh data kandidat",
    {
        "id": fields.String(readonly=True),
        "nomor_urut": fields.Integer(readonly=True),
        "nama": fields.String(readonly=True),
        "tanggal_lahir": fields.String(readonly=True),
    },
)


time_data_model = api.model(
    "Setup timestamp data",
    {
        "registerstart": fields.String(required=True),
        "registerfinis": fields.String(required=True),
        "votingstart": fields.String(required=True),
        "votingfinis": fields.String(required=True),
    },
)

message_object_model = api.model(
    "Model untuk message object",
    {"status": fields.String, "message": fields.String},
)


@api.route("/setting/waktu")
class SetupTimeController(Resource):
    @jwt_required()
    @api.doc(responses={200: "OK", 500: "Bad requests"})
    @api.expect(time_data_model)
    @api.marshal_with(message_object_model)
    def post(self):
        user_data = get_jwt()["sub"]
        data = request.json
        result = adminservice.SetupTimeData(data, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(500, result)


@api.route("/pendaftaran/pemilih")
class PemilihConntroller(Resource):
    @jwt_required()
    @api.doc(responses={200: "Oke", 500: "Internal Server Error"})
    @api.expect(pemilih_data_model)
    @api.marshal_with(message_object_model)
    def post(self):
        user_data = get_jwt()["sub"]
        data = request.json
        result = adminservice.RegisterPemilih(data, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(500, result)


@api.route("/pendaftaran/kandidat")
class KandidatController(Resource):
    @jwt_required()
    @api.doc(responses={200: "OK", 500: "Internal Server Error"})
    @api.marshal_with(message_object_model)
    @api.expect(kandidat_data_model)
    def post(self):
        user_data = get_jwt()["sub"]
        data = request.json
        result = adminservice.RegisterKandidat(data, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(500, result)


@api.route("/data/pemilih")
class DataPemilih(Resource):
    @jwt_required()
    @api.doc(responses={200: "OK", 500: "Internal Server Error"})
    @api.marshal_list_with(all_pemilih_data)
    def get(self):
        result = adminservice.GetAllPemilihData()
        if result != "Abort":
            return result
        else:
            api.abort(
                500,
                {
                    "status": "Error",
                    "message": "Terjadi kesalahan pada server",
                },
            )


@api.route("/data/kandidat")
class DataKandidat(Resource):
    @jwt_required()
    @api.doc(responses={200: "OK", 500: "Internal Server Error"})
    @api.marshal_list_with(all_kandidat_data)
    def get(self):
        result = adminservice.GetAllKandidatData()
        if result != "Abort":
            return result
        else:
            api.abort(
                500,
                {
                    "status": "Error",
                    "message": "Terjadi kesalahan pada server",
                },
            )
