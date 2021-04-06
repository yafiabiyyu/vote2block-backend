from project.models.user_model import UserDoc, UserTxHistoryDoc
from project.service.enkripsi_service import DataEncryption
from project.service.ethereum_service import EthereumService

de = DataEncryption()
es = EthereumService()

class UserInfo:
    def GetUserInfo(self, user_data):
        data = UserDoc.objects(username=user_data).first()
        return data
    
    def GetUserData(self, user_data):
        data = UserDoc.objects(username=user_data).first()
        user_address = data.ethereum['ethereum_address']
        user_access = de.Decrypting(
            data.ethereum['ethereum_access'].encode()
        )
        return user_address, user_access

    def SaveUserTx(self,username_data, tx_hash, signature):
        data_user = UserDoc.objects(username=username_data).first()
        history = UserTxHistoryDoc(
            user_data=data_user.to_dbref(),
            tx_hash=tx_hash,
            signature_data=signature
        )
        history.save()