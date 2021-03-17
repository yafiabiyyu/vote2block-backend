from project.models.user_model import UserDoc
from project.service.enkripsi_service import DataEncryption
from project.service.ethereum_service import EthereumService
from project.tasks.tasks import BroadcastTx

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
            "ethereum_wallet":eth_address,
            "ethereum_access":enc_eth_access.decode()
        }
        return eth_data
    def AddAdminPetugas(
        self,
        data,
        ketua_address,
        user_data
    ):
        get_ketua_data = UserDoc.objects(nama_lengkap=data['nama_lengkap']).first()
        if get_ketua_data is None:
            ethereum_wallet = self.WalletSetup()
            access = {
                "level":1,
                "group":"penyelenggara"
            }
            try:
                save_admin_data = UserDoc(
                    username = self.GenerateUsername(
                        data['nama_lengkap']
                    ),
                    nama_lengkap=data['nama_lengkap'],
                    contact = data['contact'],
                    alamat = data['alamat'],
                    access=access,
                    ethereum=ethereum_wallet
                )
                save_admin_data.GeneratePasswordHash(
                    self.GenerateUsername(
                        data['nama_lengkap']
                    )
                )
                save_admin_data.save()
                tx_hash = es.AddAdminPetugas(
                    ethereum_wallet['ethereum_address'],
                    ketua_address
                )
                result = BroadcastTx.delay(tx_hash, user_data)
                print(result)
            except Exception as e:
                message = {
                    "status":"Gagal",
                    "message":e
                }
                return message