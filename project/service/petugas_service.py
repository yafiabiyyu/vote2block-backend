from project.models.voting_model import Kandidat, VotingTimeStamp
from project.service.ethereum_service import EthereumService
from web3.exceptions import SolidityError
from project.service.user_info_service import UserInfo
from eth_account.messages import encode_defunct
from project.tasks.tasks import RegisterKandidat
import time

es = EthereumService()
us = UserInfo()


class PetugasService:
    def ConvertKandidatNameToBytes(self, kandidat_name):
        w3 = es.SetupW3()
        bytes_name = w3.soliditySha3(["string"], [str(kandidat_name)])
        return bytes_name.hex()

    def CheckRegisterTIme(self):
        current_timestamp = time.time()
        get_timestamp_data = VotingTimeStamp.objects().all()
        if current_timestamp < get_timestamp_data.register_start:
            message_object = {
                "status": "Gagal",
                "message": "Pendaftaran Kandidat dan Pemilih belum dibuka",
            }
            return message_object
        elif (
            current_timestamp > get_timestamp_data.register_start
            and current_timestamp < get_timestamp_data.register_finis
        ):
            message_object = {
                "status": "Berhasil",
                "message": "Pendaftaran Kandidat dan Pemilih telah dibuka",
            }
            return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Pendaftaran Kandidat dan Pemilih telah ditutup",
            }
            return message_object

    def RegisterKandidat(self, json_data, user_data):
        w3 = es.SetupW3()
        petugas_address, petugas_access = us.GetUserData(user_data)
        check_register_time = self.CheckRegisterTIme()
        check_kandidat_data = Kandidat.objects(
            nama_kandidat=json_data["nama_kandidat"]
        )
        if check_register_time == "Berhasil":
            if check_kandidat_data is None:
                try:
                    nonce = w3.eth.getTransactionCount(petugas_address)
                    bytes_kandidat_name = (
                        self.ConvertKandidatNameToBytes(
                            json_data["nama_kandidat"]
                        )
                    )
                    msg = w3.soliditySha3(
                        ["uint256", "bytes32", "uint256"],
                        [
                            int(json_data["kandidat_id"]),
                            bytes_kandidat_name,
                            nonce,
                        ],
                    )
                    message = encode_defunct(primitive=msg)
                    sign_message = w3.eth.account.sign_message(
                        message, petugas_access
                    )
                    result = RegisterKandidat.delay(
                        int(json_data["kandidat_id"]),
                        nonce,
                        bytes_kandidat_name,
                        sign_message.signature.hex(),
                    )
                    if result.wait() == "Gagal":
                        raise SolidityError
                except SolidityError:
                    message_object = {
                        "status": "Error",
                        "message": "Terjadi masalah pada server",
                    }
                    return message_object
                else:
                    save_kandidat = Kandidat(
                        nomor_urut=int(json_data["kandidat_id"]),
                        nama_kandidat=json_data["nama_kandidat"],
                        nama_bytes=bytes_kandidat_name,
                        alamat=json_data["alamat"],
                        contact=json_data["contact"],
                        image_url=json_data["image_url"],
                    )
                    save_kandidat.save()
                    us.SaveUserTx(
                        user_data, result.wait(), sign_message.hex()
                    )
                    message_object = {
                        "status": "Berhasil",
                        "message": "Kandidat berhasil di daftarkan kedalam sistem",
                    }
                    return message_object
            else:
                message_object = {
                    "status":"Gagal",
                    "message":"Kandiat sudah terdaftar di dalam sistem"
                }
                return message_object
        else:
            return check_register_time