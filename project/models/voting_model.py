from typing_extensions import Required
from project.factory import db


class KandidatDoc(db.Document):
    _id = db.StringField(required=True, primary_key=True)
    nama = db.StringField(required=True)
    nama_bytes = db.StringField(required=True)
    tgl_lahir = db.StringField(required=True)
    visi = db.StringField(required=True)
    misi = db.StringField(required=True)
    contact = db.StringField(required=True)
    alamat = db.StringField(required=True)
    image_url = db.StringField(required=True)
