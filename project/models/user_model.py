from project.factory import db
from werkzeug.security import (
    generate_password_hash,
    check_password_hash,
)


class AdminDoc(db.Document):
    _id = db.StringField(required=True, primary_key=True)
    nama_admin = db.StringField(required=True)
    username = db.StringField(required=True)
    password_hash = db.StringField(required=True, max_length=255)
    contact = db.DictField(required=True)
    alamat = db.DictField(required=True)
    ethereum = db.DictField(required=True)

    def GeneratePasswordHash(self, password):
        self.password_hash = generate_password_hash(password)

    def UpdatePassword(self, password):
        return generate_password_hash(password)

    def VerifyPassword(self, password):
        return check_password_hash(
            pwhash=self.password_hash, password=password
        )


class AdminTxHistory(db.Document):
    user_data = db.ReferenceField("AdminDoc")
    tx_hash = db.StringField(required=True)
    type_tx = db.StringField(required=True)
    tanggal_tx = db.StringField(required=True)
    signature_data = db.StringField(required=True)


class PemilihDoc(db.Document):
    _id = db.StringField(required=True, primary_key=True)
    nama_lengkap = db.StringField(required=True)
    tgl_lahir = db.StringField(required=True)
    username = db.StringField(required=True)
    password_hash = db.StringField(max_length=255, required=True)
    contact = db.DictField(required=True)
    alamat = db.DictField(required=True)
    ethereum = db.DictField(required=True)

    def GeneratePasswordHash(self, password):
        self.password_hash = generate_password_hash(password)

    def UpdatePasswordHash(self, password):
        return generate_password_hash(password)

    def VerifyPassword(self, password):
        return check_password_hash(
            pwhash=self.password_hash, password=password
        )


class PemilihTxDoc(db.Document):
    user_data = db.ReferenceField("PemilihDoc")
    tx_hash = db.StringField(required=True)
    type_tx = db.StringField(required=True)
    tanggal_tx = db.StringField(required=True)
    signature_data = db.StringField(required=True)


class RevokedTokenDoc(db.Document):
    jti = db.StringField(max_length=120)

    def IsJtiBlackListed(jti):
        Query = RevokedTokenDoc.objects(jti=jti).first()
        return bool(Query)
