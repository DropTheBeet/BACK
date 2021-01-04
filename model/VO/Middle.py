from model import db

class Middle(db.Model):
    __tablename__ = 'middle'

    middle_no = db.Column(db.Integer, primary_key=True)
    c_middle = db.Column(db.String(20), nullable=False)