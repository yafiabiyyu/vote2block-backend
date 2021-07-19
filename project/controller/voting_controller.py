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
        "misi": fields.String,
        "image_url":fields.String
    }
)

quick_count_mode = api.model(
    "Model untuk Perhitungan suara sementara",
    {
        "nama_kandidat": fields.String(readonly=True),
        "total_suara": fields.Integer(readonly=True),
    },
)

data_kandidat = {}
data_kandidat['nomor_urut'] = fields.String(attribute="nomor_urut")
data_kandidat['nama'] = fields.String(attribute="nama")
data_kandidat['visi'] = fields.String(attribute="visi")
data_kandidat['misi'] = fields.String(attribute="misi")
data_kandidat['image_url'] = fields.String(attribute="image_url")

bukti_pemilihan_model = api.model(
    "Model untuk bukti pemilihan",
    {
        "status":fields.String, 
        "message":fields.String,
        "tx_hash":fields.String(skip_none=True),
        "data":fields.Nested(data_kandidat, skip_none=True)
    }
)

hasil_pemilihan_model = api.model(
    "Model untuk hasil pemilihan",
    {
        "status":fields.String,
        "message":fields.String,
        "data":fields.Nested(data_kandidat, skip_none=True)
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
        if result['status'] == "Berhasil":
            return result
        else:
            return result

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

@api.route("/kandidat/dipilih")
class KandidatDipilih(Resource):
    @jwt_required()
    @marshal_with(bukti_pemilihan_model)
    @api.doc(responses={200:"OK", 500:"Internal server error"})
    def get(self):
        user_data = get_jwt()['sub']
        try:
            result = voting.GetKandidatTerpilih(user_data)
            return result
        except Exception as e:
            api.abort(500, e)
