from project.models.user_model import UserDoc
from project.service.enkripsi_service import DataEncryption
from project.service.ethereum_service import EthereumService
from project.service.user_info_service import UserInfo
from project.tasks.tasks import SavePetugasToContract,RemovePetugasFromContract
from eth_account.messages import encode_defunct
from celery.result import AsyncResult
from datetime import datetime

de = DataEncryption()
es = EthereumService()
us = UserInfo()

class KetuaService:
    def GenerateUsername(self, data):
        username = data.replace(" ", "")
        return username.lower()
    
    def AddPetugas(self, json_data, user_data):
        w3 = es.SetupW3()
        petugas_address, petugas_access = es.CreateWallet()
        ketua_address, ketua_access = us.GetUserData(user_data)
        petugas_data = UserDoc.objects(nama_lengkap=json_data['nama_lengkap']).first()
        username = self.GenerateUsername(json_data['nama_lengkap'])
        access = {
            "level":"petugas",
            "status":"aktif"
        }
        if petugas_data is None:
            try:
                save_petugas = UserDoc(
                    username=username,
                    nama_lengkap=json_data['nama_lengkap'],
                    contact=json_data['contact'],
                    alamat=json_data['alamat'],
                    access=access,
                    ethereum = {
                        "ethereum_address":petugas_address,
                        "ethereum_access":petugas_access.decode()
                    }
                )
                save_petugas.GeneratePasswordHash(username)
                save_petugas.save()

                # create signature message
                ketua_nonce = w3.eth.getTransactionCount(ketua_address)
                msg = w3.soliditySha3(
                    ['address', 'uint256'],
                    [
                        w3.toChecksumAddress(petugas_address),
                        ketua_nonce
                    ]
                )
                message = encode_defunct(primitive=msg)
                sign_message = w3.eth.account.sign_message(message, ketua_access)
                result = SavePetugasToContract.delay(
                    w3.toChecksumAddress(petugas_address),
                    sign_message.signature.hex(),
                    ketua_nonce
                )
                us.SaveUserTx(user_data, result.wait(), sign_message.signature.hex())
                message_object = {
                    "status":"Berhasil",
                    "message":"Petugas {} berhasil ditambahkan".format(json_data['nama_lengkap'])
                }
                return message_object
            except Exception as e:
                message_object = {
                    "status":"Error",
                    "message":e
                }
                return message_object
        else:
            message_object = {
                "status":"Gagal",
                "message":"Pengguna {} telah terdaftar".format(json_data['nama_lengkap'])
            }
            return message_object
    
    def RemovePetugas(self, petugasId, user_data):
        w3 = es.SetupW3()
        ketua_address, ketua_access = us.GetUserData(user_data)
        get_petugas_data = UserDoc.objects(id=str(petugasId)).first()
        access = {
            "level":"None",
            "status":"nonaktif"
        }
        if get_petugas_data.access['status'] == "aktif":
            try:
                # update access petugas menjadi nonaktif
                remove_admin = UserDoc.objects(id=str(petugasId)).update(access=access)

                # membuat signature message menghapus petugas dari smartcontract
                ketua_nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(ketua_address))
                msg = w3.soliditySha3(
                    ['address', 'uint256'],
                    [
                        w3.toChecksumAddress(get_petugas_data.ethereum['ethereum_address']),
                        ketua_nonce
                    ]
                )
                message = encode_defunct(primitive=msg)
                sign_message = w3.eth.account.sign_message(message, ketua_access)
                result = RemovePetugasFromContract.delay(
                    w3.toChecksumAddress(get_petugas_data.ethereum['ethereum_address']),
                    sign_message.signature.hex(),
                    ketua_nonce
                )
                us.SaveUserTx(user_data, result.wait(), sign_message.signature.hex())
                message_object = {
                    "status":"Berhasil",
                    "message":"Petugas {} berhasil di hapus".format(get_petugas_data.nama_lengkap)
                }
                return message_object
            except Exception as e:
                message_object = {
                    "status":"Error",
                    "message":e
                }
        else:
            message_object = {
                "status":"Gagal",
                "message":"Petugas {} tidak terdaftar dalam sistem".format(get_petugas_data.nama_lengkap)
            }
            return message_object
    
    def GetAllPetugas(self):
        try:
            data_list = []
            data = UserDoc.objects(access={"level":"petugas","status":"aktif"}).all()
            for user in data:
                data_list.append({
                    "id":user.id,
                    "nama_lengkap":user.nama_lengkap,
                    "status":user.access['status'],
                    "level":user.access['level'],
                    "ethereum_address":user.ethereum['ethereum_address']
                })
            return data_list
        except Exception as e:
            message_object = {
                "status":"Error",
                "message":e
            }
            return e
    
    def GetOnePetugas(self, petugasId):
        user = UserDoc.objects(id=str(petugasId)).first()
        return user