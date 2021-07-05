from flask import request
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt
from project.service.voting_srvice import VotingService

voting = VotingService()
api = Namespace("Voting Controller", "Endpoint untuk voting")

voting_data_model = api.model(
    "Model untuk voting controller",
    {"kandidatId": fields.Integer(requied=True)},
)

message_object_model = api.model(
    "Model untuk message object",
    {
        "status": fields.String(readonly=True),
        "message": fields.String(readonly=True),
    },
)

quick_count_mode = api.model(
    "Model untuk Perhitungan suara sementara",
    {
        "nomor_urut": fields.Integer(readonly=True),
        "nama_kandidat": fields.String(readonly=True),
        "visi": fields.String(readonly=True),
        "misi": fields.String(readonly=True),
        "total_suara": fields.Integer(readonly=True),
    },
)

hasil_pemilihan_model = api.model(
    "Model untuk hasil pemilihan",
    {
        "nomor_urut": fields.Integer,
        "nama_kandidat": fields.String,
        "image_url": fields.String,
    },
)


@api.route("/kandidat")
class VotingKandidat(Resource):
    @jwt_required()
    @api.doc(responses={200: "OK", 500: "Internal server error"})
    @api.expect(voting_data_model)
    @api.marshal_with(message_object_model)
    def post(self):
        user_data = get_jwt()["sub"]
        json_data = request.json
        result = voting.Voting(json_data, user_data)
        if (
            result["status"] == "Berhasil"
            or result["status"] == "Gagal"
        ):
            return result
        else:
            api.abort(500, result)

    @jwt_required()
    @api.doc(responses={200: "Ok", 400: "Bad Request"})
    @api.marshal_with(message_object_model)
    def get(self):
        user_data = get_jwt()["sub"]
        result = voting.CheckVoting(user_data)
        return result


@api.route("/quickcount")
class QuickController(Resource):
    @jwt_required()
    @api.doc(responses={200: "OK", 400: "Bad Requests"})
    @api.marshal_list_with(quick_count_mode)
    def get(self):
        result = voting.QuickCount()
        if result != "Abort":
            return result
        else:
            api.abort(
                400,
                {
                    "status": "Gagal",
                    "message": "Terjadi kesalahan pada server",
                },
            )

@api.route('/hasil/pemilihan')
class HasilPemilihan(Resource):
    @jwt_required()
    @api.doc(responses={200:"OK", 500:"Internal server error"})
    def get(self):
        hasil = voting.HasilPemilihan()
        if hasil == "Abort":
            api.abort(500, hasil)
        else:
            return hasil

@api.route('/check/waktu/pendaftaran')
class CheckWaktuPendaftaran(Resource):
    @jwt_required()
    @api.marshal_with(message_object_model)
    @api.doc(responses={200:"OK", 500:"Internal server Error"})
    def get(self):
        result = voting.CheckRegister()
        return result

@api.route('/check/waktu')
class CheckWaktu(Resource):
    @jwt_required()
    @api.marshal_with(message_object_model)
    @api.doc(responses={200:"OK", 500:"Internal server Error"})
    def get(self):
        result = voting.getWaktuData()
        return result