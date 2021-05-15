from project.factory import db


class VotingTimeStamp(db.Document):
    register_start = db.StringField(required=True)
    register_finis = db.StringField(required=True)
    voting_start = db.StringField(required=True)
    voting_finis = db.StringField(required=True)
