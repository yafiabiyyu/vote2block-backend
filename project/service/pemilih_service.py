from flask_mongoengine import json
from project.models.user_model import PemilihDoc
from project.tasks.tasks import GetPemilihDataTask


class PemilihService:
    def GetPemilihData(self, user_data):
        try:
            data_from_db = PemilihDoc.objects(
                username=user_data
            ).first()
            data_from_smartcontract = GetPemilihDataTask.delay(
                data_from_db.ethereum["ethereum_address"]
            )
            data_pemilih = data_from_smartcontract.get()
            data = {
                "pemilih_id": data_from_db._id,
                "nama_lengkap": data_from_db.nama_lengkap,
                "tanggal_lahir": data_from_db.tgl_lahir,
                "username": data_from_db.username,
                "contact": data_from_db.contact,
                "alamat": data_from_db.alamat,
                "ethereum_address": data_from_db.ethereum[
                    "ethereum_address"
                ],
                "hak_pilih": data_pemilih[0],
                "status_voting": data_pemilih[2],
            }
            return data
        except Exception:
            return "Error"

    def PemilihUpdatePassword(self, json_data, user_data):
        get_user_data = PemilihDoc.objects(username=user_data).first()
        if get_user_data is not None and get_user_data.VerifyPassword(
            json_data["old_password"]
        ):
            generate_new_password_hash = (
                get_user_data.UpdatePasswordHash(
                    json_data["new_password"]
                )
            )
            new_user_password_update = PemilihDoc.objects(
                username=user_data
            ).update(password_hash=generate_new_password_hash)
            message_object = {
                "status":"Berhasil",
                "message":"Password berhasil di perbarui"
            }
            return message_object
        else:
            message_object = {
                "status":"Gagal",
                "message":"Terjadi kesalahan"
            }
            return message_object
