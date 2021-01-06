from model import db
from sqlalchemy import ForeignKey

class Likes(db.Model):
    __tablename__ = 'likes'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), primary_key=True)

    def __init__(self, user_no, img_no):
        self.user_no = user_no
        self.img_no = img_no

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}