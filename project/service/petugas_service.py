from project.models.voting_model import Kandidat, VotingTimeStamp
from project.service.ethereum_service import EthereumService
from project.service.user_info_service import UserInfo
from eth_account.message import encode_defunct
from project.tasks.tasks import RegisterKandidat
from datetime import datetime
import time

es = EthereumService()
us = UserInfo()


class PetugasService:
    def GenerateBytesNama(self, nama_kandidat):
        w3 = es.SetupW3()
        name_bytes = w3.soliditySha3(["string"], [str(nama_kandidat)])
        return name_bytes

    def CheckRegisterTimeStamp(self):
        current_timestamp = time.time()
        get_timestamp = VotingTimeStamp.objects().all()
        if (
            current_timestamp > get_timestamp.register_start
            and current_timestamp > get_timestamp.register_finis
        ):
            return True
        else:
            return False

    def RegisterKandidat(self, json_data, user_data):
        w3 = es.SetupW3()
        petugas_address, petugas_access = us.GetUserData(user_data)
        get_kandidat_data = Kandidat.objects(
            nama_kandidat=json_data["nama_kandidat"]
        ).first()
        bytes_name = self.GenerateBytesNama(json_data["nama_kandidat"])
        if getkandidat_data is None:
            try:
                petugas_nonce = w3.eth.getTransactionCount(
                    w3.toChecksumAddress(petugas_address)
                )
                msg = w3.soliditySha3(
                    ["uint256", "bytes32", "uint256"],
                    [
                        int(json_data["kandidat_id"]),
                        bytes_name,
                        petugas_none,
                    ],
                )
                message = encode_defunct(primitive=msg)
                sign_message = w3.eth.account.sign_message(
                    message, petugas_access
                )
                result = RegisterKandidat.delay(
                    int(json_data["kandidat_id"]),
                    petugas_nonce,
                    bytes_name,
                    sign_message.signature.hex(),
                )
                us.SaveUserTx(
                    user_data,
                    result.wait(),
                    sign_message.signature.hex(),
                )
            except Exception as e:
                message_object = {"status": "Error", "message": e}
                return message_object
            else:
                save_kandidat_data = Kandidat(
                    nomor_urut=int(json_data["nomor_kandidat"]),
                    nama_kandidat=json_data["nama_kandidat"],
                    nama_bytes=bytes_name.hex(),
                    alamat=json_data["alamat"],
                    contact=json_data["contact"],
                )
                save_kandidat_data.save()
                message_object = {
                    "status": "Berhasil",
                    "message": "Kandidat berhasil di daftarkan",
                }
                return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Kandidat {} Telah terdaftar".format(
                    json_data["nama_kandidat"]
                ),
            }
            return message_object
