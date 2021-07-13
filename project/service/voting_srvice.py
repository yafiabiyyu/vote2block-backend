from eth_account.messages import encode_defunct
from web3.exceptions import SolidityError
import time
from project.models.user_model import PemilihDoc, PemilihTxDoc
from project.models.voting_model import KandidatDoc
from project.service.ethereum_service import EthereumService
from project.service.pemilih_service import PemilihService
from project.tasks.tasks import (
    GetKandidatData,
    GetTimeDataTask,
    GetKandidatTotalDataTask,
    KandidatTerpilihTask,
    VotingTask,
    GetPemilihDataTask,
)

es = EthereumService()
ps = PemilihService()


class VotingService:
    def getWaktuData(self):
        get_time_data = GetTimeDataTask.delay()
        time_data = get_time_data.get()
        if time_data[0] != 0:
            message_object = {
                "status": "Gagal",
                "message": "Waktu telah di tetapkan",
            }
            return message_object
        else:
            message_object = {
                "status": "Berhasil",
                "message": "Waktu belum di tetapkan",
            }
            return message_object

    def CheckRegister(self):
        livetime = int(time.time())
        get_time_data = GetTimeDataTask.delay()
        time_data = get_time_data.get()
        if livetime < time_data[0]:
            message_object = {
                "status": "Gagal",
                "message": "Waktu pendaftaran belum dimulai",
            }
            return message_object
        elif livetime > time_data[0] and livetime < time_data[1]:
            message_object = {
                "status": "Berhasil",
                "message": "Waktu pendaftaran telah dibuka",
            }
        elif livetime > time_data[1]:
            message_object = {
                "status": "Gagal",
                "message": "Waktu pendaftaran telah berakhir",
            }
            return message_object

    def CheckVoting(self, user_data):
        livetime = int(time.time())
        pemilih_data = PemilihDoc.objects(username=user_data).first()
        pemilih_address = pemilih_data.ethereum["ethereum_address"]
        get_pemilih_status = GetPemilihDataTask.delay(pemilih_address)
        pemilih_status = get_pemilih_status.get()
        get_time_data = GetTimeDataTask.delay()
        time_data = get_time_data.get()
        if (
            livetime > time_data[0]
            and livetime > time_data[2]
            and livetime < time_data[3]
        ):
            if pemilih_status[0] == 0:
                message_object = {
                    "status": "Gagal",
                    "message": "Anda tidak memiliki hak memilih",
                }
                return message_object
            else:
                if pemilih_status[2] == False:
                    message_object = {
                        "status": "Berhasil",
                        "message": "Anda berhak menggunakan hak pilih anda",
                    }
                    return message_object
                else:
                    message_object = {
                        "status": "Gagal",
                        "message": "Anda sudah memberikan hak pilih anda",
                    }
                    return message_object
        else:
            if livetime < time_data[1] or livetime < time_data[2]:
                message_object = {
                    "status": "Gagal",
                    "message": "Waktu pemilihan belum di buka",
                }
                return message_object
            else:
                message_object = {
                    "status": "Gagal",
                    "message": "Waktu pemilihan telah berakhir",
                }
                return message_object

    def Voting(self, json_data, user_data):
        w3 = es.SetupW3()
        pemilih_address, pemilih_access = ps.GetPemilihEthereumData(
            user_data
        )
        try:
            nonce = w3.eth.getTransactionCount(pemilih_address)
            msg = w3.soliditySha3(
                ["uint256", "uint256"],
                [int(json_data["kandidatId"]), nonce],
            )
            message = encode_defunct(primitive=msg)
            sign_message = w3.eth.account.sign_message(
                message, pemilih_access
            )
            result = VotingTask.delay(
                int(json_data["kandidatId"]),
                nonce,
                sign_message.signature.hex(),
            )
            if result == "Gagal":
                raise SolidityError
        except SolidityError:
            message_object = {
                "status": "Error",
                "message": "Terjadi kesalahan pada server",
            }
            return message_object
        else:
            ps.SavePemilihTxHistory(
                user_data, result.get(), sign_message.signature.hex()
            )
            message_object = {
                "status": "Berhasil",
                "message": "Anda berhasil memberikan suara anda",
            }
            return message_object

    def QuickCount(self):
        try:
            list_kandidat = []
            get_total_kandidat = GetKandidatTotalDataTask.delay()
            total_kandidat = get_total_kandidat.get()
            for data in range(int(total_kandidat)):
                get_kandidat_data = GetKandidatData.delay(data)
                kandidat_data = get_kandidat_data.get()
                kandidat_from_db = KandidatDoc.objects(
                    nomor_urut=kandidat_data[0]
                ).first()
                list_kandidat.append(
                    {
                        "nomor_urut": kandidat_from_db.nomor_urut,
                        "nama_kandidat": kandidat_from_db.nama,
                        "visi": kandidat_from_db.visi,
                        "misi": kandidat_from_db.misi,
                        "total_suara": int(kandidat_data[1]),
                    }
                )
            return list_kandidat
        except Exception:
            return "Abort"

    def HasilPemilihan(self):
        livetime = int(time.time())
        get_time_data = GetTimeDataTask.delay()
        time_data = get_time_data.get()
        if livetime > time_data[1] and livetime > time_data[3]:
            try:
                get_pemenang_data = KandidatTerpilihTask.delay()
                pemenang_data = get_pemenang_data.get()
                if pemenang_data == "Gagal":
                    raise SolidityError
            except SolidityError:
                return "Abort"
            else:
                kandidat_terpilih = KandidatDoc.objects(
                    nomor_urut=pemenang_data
                ).first()
                pemenang = {
                    "nomor_urut": kandidat_terpilih.nomor_urut,
                    "nama_kandidat": kandidat_terpilih.nama,
                    "image_url": kandidat_terpilih.image_url,
                }
                return pemenang
        elif livetime < time_data[3]:
            message_object = {
                "status": "Gagal",
                "message": "Waktu pemilihan belum berakhir",
            }
            return message_object
