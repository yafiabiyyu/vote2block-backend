from eth_account.messages import encode_defunct
from web3.exceptions import SolidityError
import time
from project.models.user_model import (
    PemilihDoc,
    AdminDoc,
    AdminTxHistory,
)
from project.models.voting_model import KandidatDoc
from project.service.ethereum_service import EthereumService
from project.service.enkripsi_service import DataEnkripsi
from project.tasks.tasks import (
    RegisterKandidatTask,
    RegisterPemilihTask,
    GetTimeDataTask,
    SetupTimestampTask
)

es = EthereumService()
ed = DataEnkripsi()


class AdminService:
    # Fungsi untuk mengambil informsi mengenai admin
    def GetAdminData(self, user_data):
        user_data = AdminDoc.objects(username=user_data).first()
        return user_data

    def GetAdminEthereumData(self, user_data):
        data = AdminDoc.objects(username=user_data).first()
        user_access = ed.Dekripsi(
            data.ethereum["ethereum_access"].encode()
        )
        return data.ethereum["ethereum_address"], user_access

    def GetAdminTxHistory(self, user_data):
        user = AdminDoc.objects(username=user_data).first()
        get_admin_history = list(AdminTxHistory(user_data=user).all())
        return get_admin_history

    def SaveAdminTx(self, adminUsername, tx_hash, signature):
        user = AdminDoc.objects(username=adminUsername).first()
        history_tx = AdminTxHistory(
            user_data=user,
            tx_hash=tx_hash,
            signature_data=signature,
        )
        history_tx.save()

    def GeneratePemilihUsername(self, data):
        username = data.replace(" ", "")
        return username.lower()

    def ConvertKandidatNameToBytes(slef, kandidat_name):
        w3 = es.SetupW3()
        kandidat_name_bytes = w3.soliditySha3(
            ["string"], [str(kandidat_name)]
        )
        return kandidat_name_bytes.hex()

    def CheckRegisterTimeStatus(self):
        livetime = int(time.time())
        data = GetTimeDataTask.delay()
        time_status = data.get()
        if livetime < time_status[0]:
            message_object = {
                "status": "Gagal",
                "message": "Register pemilih & kandidat belum dibuka",
            }
            return message_object
        elif livetime > time_status[0] and livetime < time_status[1]:
            message_object = {
                "status": "Berhasil",
                "message": "Register pemilih & kandidat telah dibuka",
            }
            return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Register pemilih & kandidat telah ditutup",
            }
            return message_object

    def SetupTimeData(self, json_data, admin_data):
        w3 = es.SetupW3()
        admin_address, admin_access = self.GetAdminEthereumData(
            admin_data
        )
        try:
            nonce = w3.eth.getTransactionCount(admin_address)
            msg = w3.soliditySha3(
                ["uint256", "uint256", "uint256", "uint256", "uint256"],
                [
                    int(json_data["registerstart"]),
                    int(json_data["registerfinis"]),
                    int(json_data["votingstart"]),
                    int(json_data["votingfinis"]),
                    nonce,
                ],
            )
            message = encode_defunct(primitive=msg)
            sign_message = w3.eth.account.sign_message(message, admin_access)
            result = SetupTimestampTask.delay(
                int(json_data['registerstart']),
                int(json_data['registerfinis']),
                int(json_data['votingstart']),
                int(json_data['votingfinis']),
                nonce,
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
            self.SaveAdminTx(
                admin_data,
                result.get(),
                sign_message.signature.hex()
            )
            message_object = {
                "status":"Berhasil",
                "message":"Data waktu berhasil di simpan"
            }
            return message_object

    def RegisterKandidat(self, json_data, admin_data):
        w3 = es.SetupW3()
        admin_address, admin_access = self.GetAdminEthereumData(
            admin_data
        )
        check_register_time_data = self.CheckRegisterTimeStatus()
        chechk_kandidat_data = KandidatDoc.objects(
            _id=str(json_data["kandidat_id"])
        ).first()
        if check_register_time_data["status"] == "Berhasil":
            if chechk_kandidat_data is None:
                try:
                    nonce = w3.eth.getTransactionCount(admin_address)
                    kandidat_bytesName = (
                        self.ConvertKandidatNameToBytes(
                            json_data["nama_kandidat"]
                        )
                    )
                    msg = w3.soliditySha3(
                        ["uint256", "bytes32", "uint256"],
                        [
                            int(json_data["nomor_urut"]),
                            kandidat_bytesName,
                            nonce,
                        ],
                    )
                    message = encode_defunct(primitive=msg)
                    sign_message = w3.eth.account.sign_message(
                        message, admin_access
                    )
                    result = RegisterKandidatTask.delay(
                        int(json_data["nomor_urut"]),
                        kandidat_bytesName,
                        nonce,
                        sign_message.signature.hex(),
                    )
                    if result.get() == "Gagal":
                        raise SolidityError
                except SolidityError:
                    message_object = {
                        "status": "Error",
                        "message": "Terjadi kesalahan pada server",
                    }
                    return message_object
                else:
                    save_new_kandidat = KandidatDoc(
                        _id=json_data["kandidat_id"],
                        nomor_urut=json_data["nomor_urut"],
                        nama=json_data["nama_kandidat"],
                        nama_bytes=kandidat_bytesName,
                        tgl_lahir=json_data["tanggal_lahir"],
                        visi=json_data["visi"],
                        misi=json_data["misi"],
                        contact=json_data["contact"],
                        alamat=json_data["alamat"],
                        image_url=json_data["image_url"],
                    )
                    save_new_kandidat.save()
                    self.SaveAdminTx(
                        admin_data,
                        result.get(),
                        sign_message.signature.hex(),
                    )
                    message_object = {
                        "status": "Berhasil",
                        "message": "Kandidat berhasil ditambahkan kedalam sistem",
                    }
                    return message_object
            else:
                message_object = {
                    "status": "Gagal",
                    "message": "Kandidat telah terdaftar di dalam sistem",
                }
                return message_object
        else:
            return check_register_time_data

    def RegisterPemilih(self, json_data, admin_data):
        w3 = es.SetupW3()
        admin_address, admin_access = self.GetAdminEthereumData(
            admin_data
        )
        pemilih_address, pemilih_access = es.CreateWallet()
        check_register_time_data = self.CheckRegisterTimeStatus()
        check_pemilih_data = PemilihDoc.objects(
            _id=str(json_data["pemilih_id"])
        ).first()
        if check_register_time_data["status"] == "Berhasil":
            if check_pemilih_data is None:
                try:
                    nonce = w3.eth.getTransactionCount(admin_address)
                    msg = w3.soliditySha3(
                        ["address", "uint256"], [pemilih_address, nonce]
                    )
                    message = encode_defunct(primitive=msg)
                    sign_message = w3.eth.account.sign_message(
                        message, admin_access
                    )
                    result = RegisterPemilihTask.delay(
                        pemilih_address,
                        nonce,
                        sign_message.signature.hex(),
                    )
                    if result.get() == "Gagal":
                        raise SolidityError
                except SolidityError:
                    message_object = {
                        "status": "Error",
                        "message": "Terjadi kesalahan pada server",
                    }
                    return message_object
                else:
                    save_pemilih = PemilihDoc(
                        _id=str(json_data["pemilih_id"]),
                        nama_lengkap=json_data["nama_lengkap"],
                        tgl_lahir=json_data["tgl_lahir"],
                        username=self.GeneratePemilihUsername(
                            json_data["nama_lengkap"]
                        ),
                        contact=json_data["contact"],
                        alamat=json_data["alamat"],
                        ethereum={
                            "ethereum_address": pemilih_address,
                            "ethereum_access": pemilih_access.decode(),
                        },
                    )
                    save_pemilih.GeneratePasswordHash(self.GeneratePemilihUsername(json_data['nama_lengkap']))
                    save_pemilih.save()
                    self.SaveAdminTx(
                        admin_data,
                        result.get(),
                        sign_message.signature.hex(),
                    )
                    message_object = {
                        "status":"Berhasil",
                        "message":"Pemilih berhasil di daftarkan"
                    }
                    return message_object
            else:
                message_object = {
                    "status": "Gagal",
                    "message": "Pemilih telah terdaftar di dalam sistem",
                }
                return message_object
        else:
            return check_register_time_data
