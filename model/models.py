from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'category'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    cate_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    major_no = db.Column(db.Integer, db.ForeignKey('major.major_no'), nullable=False)
    middle_no = db.Column(db.Integer, db.ForeignKey('middle.middle_no'), nullable=False)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class Click_data(db.Model):
    __tablename__ = 'click_data'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), nullable=False)
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), nullable=False)
    type = db.Column(db.String(1), nullable=False)
    click_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


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


class Major(db.Model):
    __tablename__ = 'major'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    major_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_major = db.Column(db.String(20), nullable=False)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class Middle(db.Model):
    __tablename__ = 'middle'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    middle_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_middle = db.Column(db.String(20), nullable=False)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class R_image(db.Model):
    __tablename__ = 'recommendations'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), primary_key=True)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class Rec_tag(db.Model):
    __tablename__ = 'recognized_tag'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), nullable=False)
    tag_no = db.Column(db.Integer, db.ForeignKey('tag.tag_no'), nullable=False)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    point_x = db.Column(db.Integer)
    point_y = db.Column(db.Integer)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class Tag(db.Model):
    __tablename__ = 'tag'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    tag_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cate_no = db.Column(db.Integer, db.ForeignKey('category.cate_no'), nullable=False)
    tag = db.Column(db.String(20), nullable=False)
    tag_han = db.Column(db.String(20), nullable=False)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class Tag_pf(db.Model):

    __tablename__ = "tag_preference"
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)
    tag_no = db.Column(db.Integer, db.ForeignKey('tag.tag_no'), primary_key=True)
    preference = db.Column(db.Float, default=0)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}


class User(db.Model):
    __tablename__ = 'user'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    user_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(20), nullable=False)
    user_pw = db.Column(db.String(20), nullable=False)

    images = db.relationship('Image', backref='user')
    like_data = db.relationship('Likes', backref='l_user')
    clicks = db.relationship('Click_data', backref='user')

    def __init__(self, user_id, user_pw):
        self.user_id = user_id
        self.user_pw = user_pw

    def __repr__(self):
        return 'user_no : %s, user_id : %s, pw : %s' % (self.user_no, self.user_id, self.user_pw)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}
