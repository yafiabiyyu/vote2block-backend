from werkzeug.exceptions import NotFound
from project.models.voting_model import PemilihTxHistoryDoc, Pemilih
from project.tasks.tasks import GetPemilihDataTask
from project.service.enkripsi_service import DataEncryption
from project.service.ethereum_service import EthereumService

de = DataEncryption()
es = EthereumService()


class PemilihInfo:
    def GetUserInfo(self, user_data):
        get_user_data = Pemilih.objects(username=user_data).first()
        data_from_contract = GetPemilihDataTask.delay(get_user_data.ethereum['ethereum_address'])
        user_data = data_from_contract.get()
        data = {
            "pemilih_id":get_user_data._id,
            "nama_lengkap":get_user_data.nama_lengkap,
            "username":get_user_data.username,
            "contact":get_user_data.contact,
            "alamat":get_user_data.alamat,
            "ethereum_address":get_user_data.ethereum['ethereum_address'],
            "status_hak_pilih":user_data[0],
            "status_voting":user_data[2]
        }
        return data


    def UpdatePassword(self, user_data, json_data):
        get_user_data = Pemilih.objects(username=user_data).first()
        if get_user_data is not None and get_user_data.VerifyPassword(json_data['old_password']):
            new_password_hash = get_user_data.UpdatePassword(json_data['new_password'])
            user_data = Pemilih.objects(username=user_data).update(password_hash=new_password_hash)
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
        user = Pemilih.objects(username=user_data).first()
        get_history = list(
            PemilihTxHistoryDoc.objects(user_data=user).all()
        )
        return get_history

    def GetUserData(self, user_data):
        data = Pemilih.objects(username=user_data).first()
        user_address = data.ethereum["ethereum_address"]
        print(data.username)
        user_access = de.Decrypting(
            data.ethereum["ethereum_access"].encode()
        )
        return user_address, user_access

    def SaveUserTx(self, username_data, tx_hash, signature):
        data_user = Pemilih.objects(username=username_data).first()
        history = PemilihTxHistoryDoc(
            user_data=data_user.to_dbref(),
            tx_hash=tx_hash,
            signature_data=signature,
        )
        history.save()
