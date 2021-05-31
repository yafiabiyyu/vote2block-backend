import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()


class DataEncryption:
    def __init__(self):
        self.password_key = str(os.getenv("SECRET_KEY")).encode()
        self.salt = str(os.getenv("SALT")).encode()

    def GenerateKey(self):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
            backend=default_backend(),
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.password_key))
        return key

    def Encrypting(self, data):
        key = self.GenerateKey()
        f = Fernet(key)
        encrypted_data = f.encrypt(data)
        return encrypted_data

    def Decrypting(self, encrypted_data):
        key = self.GenerateKey()
        f = Fernet(key)
        decrypting_data = f.decrypt(encrypted_data)
        return decrypting_data
