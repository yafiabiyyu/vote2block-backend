from project.models.user_model import UserDoc
from project.service.enkripsi_service import DataEncryption
from project.service.ethereum_service import EthereumService
from project.tasks.tasks import SaveAdminToContract
from eth_account.messages import encode_defunct
from celery.result import AsyncResult
import json

de = DataEncryption()
es = EthereumService()
class KetuaService:
    def GenerateUsername(self, data):
        username = data.replace(" ", "")
        return username.lower()
    def WalletSetup(self): 
        eth_access, eth_address = es.CreateWallet()
        enc_eth_access = de.Encrypting(eth_access)
        eth_data = {
            "ethereum_address":eth_address,
            "ethereum_access":enc_eth_access.decode()
        }
        return eth_address, enc_eth_access.decode()
    def AddAdminPetugas(self, json_data, user_data):
        get_admin_data = UserDoc.objects(nama_lengkap=json_data['nama_lengkap']).first()
        w3 = es.SetupW3()
        if get_admin_data is None:
            user_address, eth_access = self.WalletSetup()
            access = {
                "level":1,
                "group":"penyelenggara"
            }
            try:
                save_admin = UserDoc(
                    username=self.GenerateUsername(json_data['nama_lengkap']),
                    nama_lengkap=json_data['nama_lengkap'],
                    contact=json_data['contact'],
                    alamat=json_data['alamat'],
                    access=access,
                    ethereum={"ethereum_address":user_address,"ethereum_access":eth_access}
                )
                save_admin.GeneratePasswordHash(
                    self.GenerateUsername(json_data['nama_lengkap'])
                )
                save_admin.save()

                # ketua membuat signature message
                address, access = es.GetEthAccess(user_data)
                ketua_nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(address))
                msg = w3.soliditySha3(
                    ['address','uint256'],
                    [
                        w3.toChecksumAddress(user_address),
                        ketua_nonce
                    ]
                )
                message = encode_defunct(primitive=msg)
                sign_message = w3.eth.account.sign_message(message,access)
                result = SaveAdminToContract.delay(
                    user_address,
                    sign_message.signature.hex(),
                    ketua_nonce
                )
                print(result.wait())
                message_object = {
                    "status":"Berhasil",
                    "admin_address":user_address,
                    "signature":sign_message.signature.hex()
                }
                return message_object
            except Exception as e:
                return {"status":"Gagal","message":e}