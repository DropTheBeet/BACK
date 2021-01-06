from model import db
from sqlalchemy import ForeignKey
from datetime import datetime

class Image(db.Model):
    __tablename__ = 'image'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    img_no = db.Column(db.Integer, primary_key=True, autoincrement=True)            # 이미지 번호
    filename = db.Column(db.String(100), nullable=False)                            # 파일명
    reg_date = db.Column(db.DateTime, nullable=False, default=datetime.now)         # 등록일
    img_url = db.Column(db.String(200))                                              # 원본 url
    thum_url = db.Column(db.String(200))                                             # 썸네일 url
    img_w = db.Column(db.Integer)                                                    # 이미지 너비
    img_h = db.Column(db.Integer)                                                    # 이미지 높이
    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), nullable=False)   # 사용자 번호

    likes = db.relationship('Likes', backref='image')
    rts = db.relationship('Rec_tag', backref='image')

    def __init__(self, filename, img_url, thum_url, img_w, img_h, user_no):
        self.filename = filename
        self.img_url = img_url
        self.thum_url = thum_url
        self.img_w = img_w
        self.img_h = img_h
        self.user_no = user_no

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
