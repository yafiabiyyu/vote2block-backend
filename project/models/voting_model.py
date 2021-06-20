from project.factory import db


class KandidatDoc(db.Document):
    _id = db.StringField(required=True, primary_key=True)
    nomor_urut = db.IntField(required=True)
    nama = db.StringField(required=True)
    nama_bytes = db.StringField(required=True)
    tgl_lahir = db.StringField(required=True)
    visi = db.StringField(required=True)
    misi = db.StringField(required=True)
    contact = db.DictField(required=True)
    alamat = db.DictField(required=True)
    image_url = db.StringField(required=True)
