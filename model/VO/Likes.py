from model import db

class Likes(db.Model):
    __tablename__ = 'likes'

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), nullable=False)