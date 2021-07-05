from eth_account.messages import encode_defunct
from web3.exceptions import SolidityError
import time
from datetime import datetime as dt
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
    SetupTimestampTask,
)

es = EthereumService()
ed = DataEnkripsi()

class AdminService:
    def GetAdminData(self, user_data):
        user_data = AdminDoc.objects(username=user_data).first()
        return user_data

    def GetAdminEthereumData(self, user_data):
        data = AdminDoc.objects(username=user_data).first()
        user_access = ed.Dekripsi(
            data.ethereum["ethereum_access"].encode()
        )
        return data.ethereum["ethereum_address"], user_access
    
    def SaveAdminTx(self, admin_username, tx_hash, typeTx, signature):
        admin = AdminDoc.objects(username=admin_username).first()
        save_tx = AdminTxHistory(
            user_data = admin,
            tx_hash = tx_hash,
            type_tx = typeTx,
            tanggal_tx = dt.today().strftime("%Y-%m-%d"),
            signature_data = signature
        )
        save_tx.save()
    
    # Fungsi untuk handle generate username pemilih
    def GeneratePemilihUsername(self, data):
        username = data.replace(" ", "")
        return username.lower()

    # Fungsi untuk merubah nama kandidat kedalam bentuk bytes32
    def ConvertKandidatNameToBytes(slef, kandidat_name):
        w3 = es.SetupW3()
        kandidat_name_bytes = w3.soliditySha3(
            ["string"], [str(kandidat_name)]
        )
        return kandidat_name_bytes.hex()
    
    # Pengaturan waktu, register pemilih, register kandidat
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
            sign_message = w3.eth.account.sign_message(
                message, admin_access
            )
            result = SetupTimestampTask.delay(
                int(json_data["registerstart"]),
                int(json_data["registerfinis"]),
                int(json_data["votingstart"]),
                int(json_data["votingfinis"]),
                nonce,
                sign_message.signature.hex(),
            )
            if result == "Gagal":
                raise SolidityError
        except SolidityError:
            message_object = {
                "status": "Error",
                "message": "Terjadi kesalahan pada server",
            }
            return message_object
        else:
            self.SaveAdminTx(
                admin_data, result.get(),'Pengaturan Waktu' ,sign_message.signature.hex()
            )
            message_object = {
                "status": "Berhasil",
                "message": "Data waktu berhasil di simpan",
            }
            return message_object
    
    def RegisterKandidat(self, json_data, admin_data):
        w3 = es.SetupW3()
        admin_address, admin_access = self.GetAdminEthereumData(
            admin_data
        )
        chechk_kandidat_data = KandidatDoc.objects(
            _id=str(json_data["kandidat_id"])
        ).first()
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
                    'Pendaftaran Kandiadt',
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

    def RegisterPemilih(self, json_data, admin_data):
        w3 = es.SetupW3()
        admin_address, admin_access = self.GetAdminEthereumData(
            admin_data
        )
        pemilih_address, pemilih_access = es.CreateWallet()
        check_pemilih_data = PemilihDoc.objects(
            _id=str(json_data["pemilih_id"])
        ).first()
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
                save_pemilih.GeneratePasswordHash(
                    self.GeneratePemilihUsername(
                        json_data["nama_lengkap"]
                    )
                )
                save_pemilih.save()
                self.SaveAdminTx(
                    admin_data,
                    result.get(),
                    'Register Pemilih',
                    sign_message.signature.hex(),
                )
                message_object = {
                    "status": "Berhasil",
                    "message": "Pemilih berhasil di daftarkan",
                }
                return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Pemilih telah terdaftar di dalam sistem",
            }
            return message_object
    def GetAllPemilihData(self):
        try:
            list_pemilih_data = []
            pemilih_data = PemilihDoc.objects().all()
            for user in pemilih_data:
                list_pemilih_data.append(
                    {
                        "id": user.id,
                        "nama_lengkap": user.nama_lengkap,
                        "tanggal_lahir": user.tgl_lahir,
                    }
                )
            return list_pemilih_data
        except Exception:
            return "Abort"

    def GetSinglePemilihData(self, pemilihId):
        data = PemilihDoc.objects(_id=str(pemilihId)).first()
        if data is not None:
            pemilih_data = {
                "pemilih_id": data._id,
                "nama_lengkap": data.nama_lengkap,
                "tanggal_lahir": data.tgl_lahir,
                "contact": data.contact,
                "alamat": data.alamat,
            }
            return pemilih_data
        else:
            return "Abort"

    def GetSingleKandidatData(self, kandidatId):
        data = KandidatDoc.objects(_id=str(kandidatId)).first()
        if data is not None:
            kandidat_data = {
                "kandidat_id": data._id,
                "nomor_urut": data.nomor_urut,
                "nama_kandidat": data.nama,
                "tanggal_lahir": data.nama,
                "visi": data.visi,
                "misi": data.misi,
                "contact": data.contact,
                "alamat": data.alamat,
                "image_url": data.image_url,
            }
            return kandidat_data
        else:
            return "Abort"

    def GetAllKandidatData(self):
        try:
            list_data_kandidat = []
            kandidat_data = KandidatDoc.objects().all()
            for kandidat in kandidat_data:
                list_data_kandidat.append(
                    {
                        "id": kandidat._id,
                        "nomor_urut": kandidat.nomor_urut,
                        "nama": kandidat.nama,
                        "tanggal_lahir": kandidat.tgl_lahir,
                    }
                )
            return list_data_kandidat
        except Exception:
            return "Abort"
    
    def GetAdminDashboard(self):
        total_pemilih = PemilihDoc.objects().all().count()
        total_kandidat = KandidatDoc.objects().all().count()
        w3 = es.SetupW3()
        system_balance = w3.fromWei(w3.eth.get_balance(w3.eth.defaultAccount), 'ether')
        message_object={
            "status":"Berhasil",
            "data":{
            "total_pemilih":total_pemilih,
            "total_kandidat":total_kandidat,
            "ethereum_balance":system_balance
            }
        }
        return message_object