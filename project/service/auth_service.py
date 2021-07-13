from project.models.user_model import (
    AdminDoc,
    PemilihDoc,
    RevokedTokenDoc,
)
from flask_jwt_extended import create_access_token, create_refresh_token


class AuthService:
    def AdminLoginService(self, json_data):
        get_admin_data = AdminDoc.objects(
            username=json_data["username"]
        ).first()
        if get_admin_data is not None:
            if get_admin_data.VerifyPassword(json_data["password"]):
                access_token = create_access_token(
                    json_data["username"]
                )
                refresh_token = create_refresh_token(
                    json_data["username"]
                )
                message_object = {
                    "status": "Berhasil",
                    "message": "Admin berhasil login",
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
        else:
            message_object = {
                "status": "Not Found",
                "message": "Data admin tidak ditemukan",
            }
            return message_object

    def PemilihLoginService(self, json_data):
        get_pemilih_data = PemilihDoc.objects(
            username=json_data["username"]
        ).first()
        if get_pemilih_data is not None:
            if get_pemilih_data.VerifyPassword(json_data["password"]):
                access_token = create_access_token(
                    json_data["username"]
                )
                refresh_token = create_refresh_token(
                    json_data["username"]
                )
                message_object = {
                    "status": "Berhasil",
                    "message": "Pemilih berhasil login",
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
        else:
            message_object = {
                "status": "Gagal",
                "message": "Data pemilih tidak ditemukan",
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
