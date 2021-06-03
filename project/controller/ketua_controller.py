from flask import request, jsonify
from flask_restx import Resource, Namespace, fields, marshal_with
from flask_jwt_extended import jwt_required, get_jwt
from project.service.ketua_service import KetuaService

api = Namespace(
    "Ketua Penyelenggara", "Endpoint untuk ketua penyelenggara"
)
ks = KetuaService()

all_petugas_data_model = api.model(
    "Petugas Data",
    {
        "id": fields.String,
        "nama_lengkap": fields.String,
        "status": fields.String,
        "level": fields.String,
        "ethereum_address": fields.String,
    },
)

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

single_petugas_data = api.model(
    "Single Petugas Data",
    {
        "nama_lengkap": fields.String,
        "username": fields.String,
        "contact": fields.Nested(contact),
        "alamat": fields.Nested(alamat),
        "access": fields.Nested(access),
        "ethereum": fields.Nested(ethereum),
    },
)

message_object = api.model(
    "Message Object Model",
    {"status": fields.String, "message": fields.String},
)

voting_timestamp_model = api.model(
    "Model Untuk Timestamp Voting & Register",
    {
        "registerstart": fields.String(required=True),
        "registerfinis": fields.String(required=True),
        "votingstart": fields.String(require=True),
        "votingfinis": fields.String(require=True)
    }
)


@api.route("/manage/petugas")
class ManagePetugas(Resource):
    @jwt_required()
    @api.marshal_with(message_object)
    @api.doc(responses={200: "OK", 400: "Error"})
    def post(self):
        user_data = get_jwt()["sub"]
        json_data = request.json
        result = ks.RegisterPetugas(json_data, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(400, result)

    @jwt_required()
    @api.marshal_list_with(all_petugas_data_model, envelope="data")
    @api.doc(responses={200: "OK", 500: "Internal Server Error"})
    def get(self):
        try:
            data = ks.GetAllPetugasData()
            if data == "Abort":
                raise Exception
            return data
        except Exception as e:
            message_object = {
                "status": "Error",
                "message": "Terjadi kesalahan pada server",
            }
            api.abort(500, message_object)


@api.route("/manage/petugas/<petugasId>")
class ManageSinglePetugas(Resource):
    @jwt_required()
    @marshal_with(single_petugas_data, envelope="data")
    def get(self, petugasId):
        try:
            result = ks.GetSinglePetugasData(petugasId)
            return result
        except Exception as e:
            api.abort(400, e)

    @jwt_required()
    def delete(self, petugasId):
        user_data = get_jwt()["sub"]
        result = ks.RemovePetugas(petugasId, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(500, result["message"])


@api.route("/manage/voting/schedule")
class ManageSchedule(Resource):
    @jwt_required()
    @api.expect(voting_timestamp_model)
    def post(self):
        user_data = get_jwt()["sub"]
        json_data = request.json
        result = ks.SetupVotingAndRegisterTime(json_data, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return jsonify(result)
        else:
            api.abort(500, result["message"])
