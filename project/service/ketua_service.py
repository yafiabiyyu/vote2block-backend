from project.models.user_model import UserDoc
from project.service.enkripsi_service import DataEncryption
from project.service.ethereum_service import EthereumService
from project.service.user_info_service import UserInfo
from project.tasks.tasks import SaveAdminToContract
from eth_account.messages import encode_defunct
from celery.result import AsyncResult
from datetime import datetime

de = DataEncryption()
es = EthereumService()
us = UserInfo()

class KetuaService:
    def GenerateUsername(self,data):
        username = data.replace(" ","")
        return username.lower()
    
    def AddAdminPetugas(self, json_data, user_data):
        w3 = es.SetupW3()
        admin_address, admin_access = es.CreateWallet()
        ketua_address, ketua_access = us.GetUserData(user_data)
        admin_data = UserDoc.objects(nama_lengkap=json_data['nama_lengkap']).first()
        username = self.GenerateUsername(json_data['nama_lengkap'])
        access = {
            "level":"1",
            "group":"penyelenggara"
        }
        if admin_data is None:
            try:
                save_admn = UserDoc(
                    username=username,
                    nama_lengkap=json_data['nama_lengkap'],
                    contact=json_data['contact'],
                    alamat=json_data['alamat'],
                    access=access,
                    ethereum={
                        "ethereum_address":admin_address,
                        "ethereum_access":admin_access
                    }
                )
                save_admn.GeneratePasswordHash(username)
                save_admn.save()

                # Create signature message
                ketua_nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(ketua_address))
                msg = w3.soliditySha3(
                    ['address','uint256'],
                    [
                        w3.toChecksumAddress(admin_address),
                        ketua_nonce
                    ]
                )
                message = encode_defunct(primitive=msg)
                sign_message = w3.eth.account.sign_message(message,ketua_access)
                result = SaveAdminToContract.delay(
                    admin_address,
                    sign_message.signature.hex(),
                    ketua_nonce
                )
                sign_hex = sign_message.signature.hex()
                us.SaveUserTx(user_data, result.wait(),sign_hex)
                message_object = {
                    "status":"Berhasil",
                    "admin_address":admin_address,
                    "signature":sign_hex
                }
                return message_object
            except Exception as e:
                return {"status":"Error","message":e}
        else:
            message_object = {
                "status":"Gagal",
                "message":"User telah terdaftar"
            }
            return message_object
