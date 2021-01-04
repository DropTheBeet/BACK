from model import db

class User(db.Model):
    __tablename__ = 'user'

    user_no = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), nullable=False)
    user_pw = db.Column(db.String(20), nullable=False)
    images = db.relationship('image', backref='user')