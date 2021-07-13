from flask import request
from flask_restx import Resource, Namespace, fields
from flask_jwt_extended import jwt_required, get_jwt
from flask_restx.marshalling import marshal_with
from project.service.voting_srvice import VotingService

voting = VotingService()
api = Namespace("Voting Controller", "Endpoint untuk voting")


message_object_model = api.model(
    "Model untuk message object",
    {
        "status":fields.String,
        "message":fields.String
    }
)

hasil_pemilihan_model = api.model(
    "Model untuk hasil pemilihan",
    {
        "nomor_urut": fields.Integer,
        "nama_kandidat": fields.String,
        "image_url": fields.String,
    },
)

voting_data_model = api.model(
    "Model untuk voting controller",
    {"kandidatId": fields.Integer(requied=True)},
)

kandidat_model = api.model(
    "Model untuk data kandidat",
    {
        "nomor_urut": fields.Integer,
        "nama": fields.String,
        "visi": fields.String,
        "misi": fields.String
    }
)

quick_count_mode = api.model(
    "Model untuk Perhitungan suara sementara",
    {
        "nama_kandidat": fields.String(readonly=True),
        "total_suara": fields.Integer(readonly=True),
    },
)

@api.route('/status/waktu')
class CheckStatusWaktu(Resource):
    @api.marshal_with(message_object_model)
    @api.doc(responses={200:"OK", 500:"Internal server error"})
    def get(self):
        result = voting.GetWaktuStatus()
        if result['status'] == "Berhasil" or result['status'] == "Gagal":
            return result
        else:
            api.abort(500, "Internal server error")

@api.route('/status/waktu/pendaftaran')
class CheckStatusWaktuPendaftaran(Resource):
    @api.marshal_with(message_object_model)
    @api.doc(responses={200:"OK", 500:"Internal server error"})
    def get(self):
        result = voting.CheckRegiserWaktu()
        if result['status'] == "Berhasil" or result['status'] == "Gagal":
            return result
        else:
            api.abort(500, "Internal server error")

@api.route('/status/waktu/pemilihan')
class CheckStatusWaktuPemilihan(Resource):
    @api.marshal_with(message_object_model)
    @api.doc(responses={200:"OK", 500:"Internal server error"})
    def get(self):
        result = voting.CheckVotingWaktu()
        if result['status'] == "Berhasil" or result['status'] == "Gagal":
            return result
        else:
            api.abort(500, "Internal server error")

@api.route("/status/pemilih")
class CheckStatusPemilih(Resource):
    @jwt_required()
    @api.marshal_with(message_object_model)
    @api.doc(responses={200:"OK", 500:"Internal server error"})
    def get(self):
        user_data = get_jwt()['sub']
        result = voting.CheckHakPilih(user_data)
        if result['status'] == "Berhasil" or result['status'] == "Gagal":
            return result
        else:
            api.abort(500, "Internal server error")

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
    
    @api.doc(responses={200: "OK", 500: "Internal server error"})
    @api.expect(voting_data_model)
    @api.marshal_list_with(kandidat_model)
    def get(self):
        result = voting.GetAllKandidatData()
        return result

@api.route("/quickcount")
class QuickController(Resource):
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
    @marshal_with(hasil_pemilihan_model)
    @api.doc(responses={200:"OK", 500:"Internal server error"})
    def get(self):
        hasil = voting.HasilPemilihan()
        if hasil == "Abort":
            api.abort(500, hasil)
        else:
            return hasil