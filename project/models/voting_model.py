from werkzeug.security import (
    generate_password_hash, 
    check_password_hash
)
from project.factory import db


class VotingTimeStamp(db.Document):
    register_start = db.StringField(required=True)
    register_finis = db.StringField(required=True)
    voting_start = db.StringField(required=True)
    voting_finis = db.StringField(required=True)


class Kandidat(db.Document):
    nomor_urut = db.IntField(required=True)
    nama_kandidat = db.StringField(required=True)
    nama_bytes = db.StringField(required=True)
    alamat = db.DictField(require=True)
    contact = db.DictField(required=True)
    image_url = db.StringField(required=True)

class Pemilih(db.Document):
    _id = db.StringField(required=True, primary_key=True)
    nama_lengkap = db.StringField(required=True)
    username = db.StringField(required=True)
    password_hash = db.StringField(max_length=255, required=True)
    contact = db.DictField(required=True)
    alamat = db.DictField(required=True)
    ethereum = db.DictField(required=True)

    def GeneratePasswordHash(self,password):
        self.password_hash = generate_password_hash(password)
    
    def UpdatePassword(self, password):
        return generate_password_hash(password)
    
    def VerifyPassword(self, password):
        return check_password_hash(
            pwhash = self.password_hash, password=password
        )