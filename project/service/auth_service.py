from project.models.user_model import UserDoc, RevokedTokenDoc
from project.models.voting_model import Pemilih
from flask_jwt_extended import create_access_token, create_refresh_token


class AuthService:
    def LoginServicePetugas(self, json_data):
        get_user_information = UserDoc.objects(
            username=json_data["username"]
        ).first()
        if get_user_information is None:
            message_object = {
                "status": "Gagal",
                "message": "User tidak ditemukan",
            }
            return message_object
        elif (
            get_user_information is not None
            and get_user_information.VerifyPassword(
                json_data["password"]
            )
        ):
            if get_user_information.access["status"] == "aktif":
                access_token = create_access_token(
                    json_data["username"]
                )
                refresh_token = create_refresh_token(
                    json_data["username"]
                )
                message_object = {
                    "status": "Berhasil",
                    "message": "User berhasil login",
                    "data": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                }
                return message_object
            else:
                message_object = {
                    "status": "Gagal",
                    "message": "Anda sudah tidak memiliki akses",
                }
                return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Username atau password salah",
            }
            return message_object

    def LoginServicePemilih(self, json_data):
        get_user_information = Pemilih.objects(
            username=json_data["username"]
        ).first()
        if get_user_information is None:
            message_object = {
                "status": "error",
                "message": "Data user tidak ditemukan",
            }
            return message_object
        elif (
            get_user_information is not None
            and get_user_information.VerifyPassword(
                json_data["password"]
            )
        ):
            access_token = create_access_token(json_data["username"])
            refresh_token = create_refresh_token(json_data["username"])
            message_object = {
                "status": "Berhasil",
                "message": "User berhasil login",
                "data": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            }
            return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Username atau password salah",
            }
            return message_object

    def LogoutService(self, jti):
        revoked_token = RevokedTokenDoc(jti=jti).save()
        if revoked_token:
            message_object = {
                "status": "Berhasil",
                "message": "Berhasil logout",
            }
            return message_object
        else:
            message_object = {
                "status": "Gagal",
                "message": "Gagal logout",
            }
            return message_object
