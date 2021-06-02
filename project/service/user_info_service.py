from project.models.user_model import UserDoc, UserTxHistoryDoc
from project.service.enkripsi_service import DataEncryption
from project.service.ethereum_service import EthereumService

de = DataEncryption()
es = EthereumService()


class UserInfo:
    def GetUserInfo(self, user_data):
        get_user_info = UserDoc.objects(username=user_data).first()
        return get_user_info

    def UpdatePassword(self, user_data, json_data):
        get_user_data = UserDoc.objects(username=user_data).first()
        if get_user_data is not None and get_user_data.VerifyPassword(json_data['old_password']):
            new_password_hash = get_user_data.UpdatePassword(json_data['new_password'])
            user_data = UserDoc.objects(username=user_data).update(password_hash=new_password_hash)
            message_object = {
                "status":"Berhasil",
                "message":"Password Berhasil di perbarui"
            }
            return message_object
        else:
            message_object = {
                "status":"Gagal",
                "message":"Terjadi kesalahan"
            }
            return message_object

    def GetUserHistoryTx(self, user_data):
        user = UserDoc.objects(username=user_data).first()
        get_history = list(
            UserTxHistoryDoc.objects(user_data=user).all()
        )
        return get_history

    def GetUserData(self, user_data):
        data = UserDoc.objects(username=user_data).first()
        user_address = data.ethereum["ethereum_address"]
        user_access = de.Decrypting(
            data.ethereum["ethereum_access"].encode()
        )
        return user_address, user_access

    def SaveUserTx(self, username_data, tx_hash, signature):
        data_user = UserDoc.objects(username=username_data).first()
        history = UserTxHistoryDoc(
            user_data=data_user.to_dbref(),
            tx_hash=tx_hash,
            signature_data=signature,
        )
        history.save()
