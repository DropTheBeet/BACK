from model import db
from sqlalchemy import ForeignKey
from datetime import datetime

class Image(db.Model):
    __tablename__ = 'image'

    img_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(100), nullable=False)
    reg_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    img_url = db.Column(db.String(200))
    thum_url = db.Column(db.String(200))
    img_w = db.Column(db.Integer)
    img_h = db.Column(db.Integer)
    user_no = db.Column(db.Integer, ForeignKey('user.user_no'), nullable=False)