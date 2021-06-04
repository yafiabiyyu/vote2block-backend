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
