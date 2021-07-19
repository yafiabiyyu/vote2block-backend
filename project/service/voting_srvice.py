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
    def GetWaktuStatus(self):
        data_from_contract = GetTimeDataTask.delay()
        time_data = data_from_contract.get()
        if time_data[0] != 0:
            message_object = {
                "status": "Gagal",
                "message": "Waktu telah di tentukan",
            }
            return message_object
        else:
            message_object = {
                "status": "Berhasil",
                "message": "Waktu belum di tentukan",
            }
            return message_object

    def CheckRegiserWaktu(self):
        livetime = int(time.time())
        data_from_contract = GetTimeDataTask.delay()
        time_data = data_from_contract.get()
        if time_data[0] == 0:
            message_object = {
                "status":"Gagal",
                "message":"Waktu pendaftaran belum di tentukan"
            }
            return message_object
        else:
            if livetime < time_data[0]:
                message_object = {
                    "status":"Gagal",
                    "message":"Waktu pendaftaran belum di mulai"
                }
                return message_object
            elif livetime > time_data[0] and livetime < time_data[1]:
                message_object = {
                    "status": "Berhasil",
                    "message": "Waktu pendaftaran telah dibuka",
                }
                return message_object
            elif livetime > time_data[1]:
                message_object = {
                    "status": "Gagal",
                    "message": "Waktu pendaftaran telah berakhir",
                }
                return message_object

    def CheckVotingWaktu(self):
        livetime = int(time.time())
        data_from_contract = GetTimeDataTask.delay()
        time_data = data_from_contract.get()
        if livetime < time_data[2]:
            message_object = {
                "status": "Gagal",
                "message": "Pemilihan belum di mulai",
            }
            return message_object
        elif livetime > time_data[2] and livetime < time_data[3]:
            message_object = {
                "status": "Berhasil",
                "message": "Pemilihan telah di mulai",
            }
            return message_object
        elif livetime > time_data[2]:
            message_object = {
                "status": "Gagal",
                "message": "Pemilihan telah berakhir",
            }
            return message_object

    def CheckHakPilih(self, user_data):
        pemilih_data = PemilihDoc.objects(username=user_data).first()
        pemilih_address = pemilih_data.ethereum["ethereum_address"]
        data_from_contract = GetPemilihDataTask.delay(pemilih_address)
        status_hakPilih = data_from_contract.get()
        if status_hakPilih[2] == False:
            message_object = {
                "status": "Berhasil",
                "message": "Anda belum menggunakan hak pilih",
            }
            return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Anda sudah menggunakan hak pilih",
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

    def GetAllKandidatData(self):
        try:
            list_data_kandidat = []
            kandidat_data = KandidatDoc.objects().all()
            for kandidat in kandidat_data:
                list_data_kandidat.append(
                    {
                        "nomor_urut": kandidat.nomor_urut,
                        "nama": kandidat.nama,
                        "visi": kandidat.visi,
                        "misi": kandidat.misi,
                        "image_url": kandidat.image_url,
                    }
                )
            return list_data_kandidat
        except Exception:
            return "Abort"

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
                        "nama_kandidat": kandidat_from_db.nama,
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
                kandidat_terpilih = KandidatDoc.objects(nomor_urut=pemenang_data).first()
                pemenang = {
                    "nomor_urut": kandidat_terpilih.nomor_urut,
                    "nama": kandidat_terpilih.nama,
                    "visi":kandidat_terpilih.visi,
                    "misi":kandidat_terpilih.misi,
                    "image_url": kandidat_terpilih.image_url,
                }
                message_object = {
                    "status":"Berhasil",
                    "message":"Data kandidat Pemenang",
                    "data": pemenang
                }
                return message_object
        elif livetime < time_data[3]:
            message_object = {
                "status": "Gagal",
                "message": "Waktu pemilihan belum berakhir",
            }
            return message_object

    def GetKandidatTerpilih(self, user_data):
        pemilih_data = PemilihDoc.objects(username=user_data).first()
        pemilih_address = pemilih_data.ethereum["ethereum_address"]
        data_from_contract = GetPemilihDataTask.delay(pemilih_address)
        kandidat_terpilih_data = data_from_contract.get()
        if kandidat_terpilih_data[1] == 0:
            tx_hash = PemilihTxDoc.objects(user_data=pemilih_data).first()
            message_object = {
                "status": "Gagal",
                "message": "Bukti pemilihan anda masih dalam proses",
                "tx_hash": "https://ropsten.etherscan.io/tx/{}".format(str(tx_hash.tx_hash))
                
            }
            return message_object
        else:
            kandidat_dipilih = KandidatDoc.objects(
                nomor_urut=kandidat_terpilih_data[1]
            ).first()
            kandidat = {
                "nomor_urut": kandidat_dipilih.nomor_urut,
                "nama": kandidat_dipilih.nama,
                "visi": kandidat_dipilih.visi,
                "misi": kandidat_dipilih.misi,
                "image_url": kandidat_dipilih.image_url,
            }
            message_object = {
                "status":"Berhasil",
                "message":"Bukti Pemilihan",
                "data":kandidat
            }
            return message_object
