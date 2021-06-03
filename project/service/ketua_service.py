from project.tasks.tasks import (
    RemovePetugasFromContract,
    SavePetugasToContract,
    SetVotingTimeStamp
)
from eth_account.messages import encode_defunct
from web3.exceptions import SolidityError
from celery.result import AsyncResult
from datetime import datetime
from project.models.user_model import UserDoc
from project.models.voting_model import VotingTimeStamp
from project.service.enkripsi_service import DataEncryption
from project.service.ethereum_service import EthereumService
from project.service.user_info_service import UserInfo


de = DataEncryption()
es = EthereumService()
us = UserInfo()


class KetuaService:
    def GenerateUsername(self, data):
        username = data.replace(" ", "")
        return username.lower()

    def RegisterPetugas(self, json_data, user_data):
        w3 = es.SetupW3()
        # mengambil ethereum address dan ethereum access ketua pelaksana
        ketua_address, ketua_access = us.GetUserData(user_data)
        user_address, user_access = es.CreateWallet()
        check_petugas_data = UserDoc.objects(
            nama_lengkap=json_data["nama_lengkap"]
        ).first()
        if check_petugas_data is None:
            try:
                nonce = w3.eth.getTransactionCount(ketua_address)
                msg = w3.soliditySha3(
                    ["address", "uint256"], [user_address, nonce]
                )
                message = encode_defunct(primitive=msg)
                sign_message = w3.eth.account.sign_message(
                    message, ketua_access
                )
                result = SavePetugasToContract.delay(
                    w3.toChecksumAddress(user_address),
                    sign_message.signature.hex(),
                    nonce,
                )
                if result.wait() == "Gagal":
                    raise SolidityError
            except SolidityError as e:
                message_object = {
                    "status": "Error",
                    "message": "Terjadi Error Pada sistem",
                }
                return message_object
            else:
                username = self.GenerateUsername(
                    json_data["nama_lengkap"]
                )
                save_new_user = UserDoc(
                    username=username,
                    nama_lengkap=json_data["nama_lengkap"],
                    contact=json_data["contact"],
                    alamat=json_data["alamat"],
                    access={"level": "petugas", "status": "aktif"},
                    ethereum={
                        "ethereum_address": user_address,
                        "ethereum_access": user_access.decode(),
                    },
                )
                save_new_user.GeneratePasswordHash(username)
                save_new_user.save()
                us.SaveUserTx(
                    user_data,
                    result.wait(),
                    sign_message.signature.hex(),
                )
                message_object = {
                    "status": "Berhasil",
                    "message": "Petugas berhasil ditambahkan kedalam sistem",
                }
                return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Petugas telah terdaftar di dalam sistem",
            }
            return message_object

    def RemovePetugas(self, petugasId, user_data):
        w3 = es.SetupW3()
        ketua_address, ketua_access = us.GetUserData(user_data)
        get_petugas_dataByID = UserDoc.objects(
            id=str(petugasId)
        ).first()
        if (
            get_petugas_dataByID is not None
            and get_petugas_dataByID.access["status"] == "aktif"
        ):
            try:
                nonce = w3.eth.getTransactionCount(ketua_address)
                msg = w3.soliditySha3(
                    ["address", "uint256"],
                    [
                        w3.toChecksumAddress(
                            get_petugas_dataByID.ethereum[
                                "ethereum_address"
                            ]
                        ),
                        nonce,
                    ],
                )
                message = encode_defunct(primitive=msg)
                sign_message = w3.eth.account.sign_message(
                    message, ketua_access
                )
                result = RemovePetugasFromContract.delay(
                    w3.toChecksumAddress(
                        get_petugas_dataByID.ethereum[
                            "ethereum_address"
                        ]
                    ),
                    sign_message.signature.hex(),
                    nonce,
                )
                if result.wait() == "Gagal":
                    raise SolidityError
            except SolidityError:
                message_object = {
                    "status": "Error",
                    "message": "Terjadi Error Pada sistem",
                }
                return message_object
            else:
                remove_petugas = UserDoc.objects(
                    id=str(petugasId)
                ).update(access={"level": "None", "status": "nonaktif"})
                us.SaveUserTx(
                    user_data,
                    result.wait(),
                    sign_message.signature.hex()
                )
                message_object = {
                    "status":"Berhasil",
                    "message":"Petugas berhasil di hapus dari sistem"
                }
                return message_object
        else:
            message_object = {
                "status":"Gagal",
                "message":"Petugas dengan ID {} tidak ditemukan".format(petugasId)
            }
            return message_object
    
    def GetAllPetugasData(self):
        try:
            list_petugas_data = []
            petugas_data = UserDoc.objects(access={"level":"petugas","status":"aktif"}).all()
            for user in petugas_data:
                list_petugas_data.append(
                    {
                        "id":user.id,
                        "nama_lengkap":user.nama_lengkap,
                        "status":user.access['status'],
                        "level":user.access['level'],
                        "ethereum_address":user.ethereum['ethereum_address']
                    }
                )
            return list_petugas_data
        except Exception as e:
            return "Abort"
    
    def GetSinglePetugasData(self, petugasId):
        petugas_data = UserDoc.objects(id=str(petugasId)).first()
        return petugas_data
    
    def SetupVotingAndRegisterTime(self, json_data, user_data):
        w3 = es.SetupW3()
        ketua_address, ketua_access = us.GetUserData(user_data)
        try:
            msg = w3.soliditySha3(
                ['uint256','uint256','uint256','uint256'],
                [
                    int(json_data['registerstart']),
                    int(json_data['registerfinis']),
                    int(json_data['votingstart']),
                    int(json_data['votingfinis'])
                ]
            )
            message = encode_defunct(primitive=msg)
            sign_message = w3.eth.account.sign_message(message,ketua_access)
            result = SetVotingTimeStamp.delay(
                int(json_data['registerstart']),
                int(json_data['registerfinis']),
                int(json_data['votingstart']),
                int(json_data['votingfinis']),
                sign_message.signature.hex()
            )
            if result == "Gagal":
                raise SolidityError
        except SolidityError:
            message_object = {
                "status":"Error",
                "message":"Terjadi kesalahan pada server"
            }
            return message_object
        else:
            save_timestamp = VotingTimeStamp(
                register_start=json_data['registerstart'],
                register_finis = json_data['registerfinis'],
                voting_start = json_data['votingstart'],
                voting_finis = json_data['votingfinis']
            )
            save_timestamp.save()
            us.SaveUserTx(
                user_data,
                result.wait(),
                sign_message.signature.hex()
            )
            message_object = {
                "status":"Berhasil",
                "message":"Waktu register dan voting berhasil di simpan"
            }
            return message_object