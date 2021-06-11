from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.fernet import Fernet
import base64, os
from dotenv import load_dotenv

load_dotenv()


class DataEnkripsi:
    def __init__(self):
        self.password_key = str(os.getenv("SECRET_KEY")).encode()
        self.salt = str(os.getenv("SALT")).encode()

    def GenerateKey(self):
        kdf = Scrypt(
            salt=self.salt,
            length=32,
            n=2**14,
            r=8,
            p=1
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password_key))
        return key

    def Enkripsi(self, data):
        key = self.GenerateKey()
        f = Fernet(key)
        encrypted_data = f.encrypt(data)
        return encrypted_data

    def Dekripsi(self, encrypted_data):
        key = self.GenerateKey()
        f = Fernet(key)
        decrypting_data = f.decrypt(encrypted_data)
        return decrypting_data
