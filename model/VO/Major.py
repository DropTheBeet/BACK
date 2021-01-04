from model import db

class Major(db.Model):
    __tablename__ = 'major'

    major_no = db.Column(db.Integer, primary_key=True)
    c_major = db.Column(db.String(20), nullable=False)