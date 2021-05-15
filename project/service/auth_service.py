from project.models.user_model import UserDoc, RevokedTokenDoc
from flask_jwt_extended import(
    create_access_token,
    create_refresh_token
)


class AuthService:
    def LoginService(self,data):
        get_user_data = UserDoc.objects(
            username=data['username']
        ).first()
        if get_user_data is None:
            message_object = {
                'status':'Gagal',
                'message':"Username {} tidak ditemukan".format(data['username'])
            }
            return message_object
        elif get_user_data is not None and get_user_data.VerifyPassword(data['password']):
            eth_wallet = get_user_data.ethereum['ethereum_address']
            access_token = create_access_token(data['username'], additional_claims={"eth_wallet":eth_wallet})
            refresh_token = create_refresh_token(data['username'], additional_claims={"eth_wallet":eth_wallet})
            message_object = {
                'status':'Berhasil',
                'data':{
                    'jwt_token':access_token,
                    'refresh_token':refresh_token,
                    'address':eth_wallet
                }
            }
            return message_object
        else:
            return {'status':"Gagal",'message':'Username atau Password salah'}
    
    def LogoutService(self, jti):
        revoked_token = RevokedTokenDoc(jti=jti).save()
        if revoked_token:
            message_object = {
                'status':"Berhasil",
                "message":"Berhasil Logout"
            }
            return message_object