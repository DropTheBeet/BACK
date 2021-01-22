from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 객체 생성
db = SQLAlchemy()

# 분류 테이블
class Category(db.Model):
    __tablename__ = 'category'  # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}  # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    cate_no = db.Column(db.Integer, primary_key=True, autoincrement=True)                   # 분류 번호 : 정수형, 기본키, 자동 증가
    major_no = db.Column(db.Integer, db.ForeignKey('major.major_no'), nullable=False)       # 대분류 번호 : 정수형, 외래키(대분류 테이블의 대분류 번호 참조), Not null
    middle_no = db.Column(db.Integer, db.ForeignKey('middle.middle_no'), nullable=False)    # 중분류 번호 : 정수형, 외래키(중분류 테이블의 대분류 번호 참조), Not null

    tag = db.relationship('Tag', backref="category")            # 태그 테이블과 관계 생성 (Tag(클래스이름) 참조, backref : 태그 테이블에서 참조하는 이름)

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}


# 클릭 데이터 테이블
class Click_data(db.Model):
    __tablename__ = 'click_data'    # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}   # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    no = db.Column(db.Integer, primary_key=True, autoincrement=True)                # 번호 : 정수형, 기본키, 자동증가
    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), nullable=False)  # 사용자 번호 : 정수형, 외래키(사용자 테이블의 사용자 번호 참조)
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), nullable=False)   # 이미지 번호 : 정수형, 외래키(이미지 테이블의 이미지 번호 참조)
    type = db.Column(db.String(1), nullable=False)                                  # 클릭 종류 : 문자열(1) ('S':검색, 'R':추천)
    click_date = db.Column(db.DateTime, nullable=False, default=datetime.now)       # 클릭 날짜 : DateTime, 기본값 : 현재 시간

    def __init__(self, user_no, img_no, type):
        self.user_no = user_no
        self.img_no = img_no
        self.type = type

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}


# 이미지 테이블
class Image(db.Model):
    __tablename__ = 'image'     # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}   # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    img_no = db.Column(db.Integer, primary_key=True, autoincrement=True)            # 이미지 번호 : 정수형, 기본키, 자동증가
    filename = db.Column(db.String(100), nullable=False)                            # 파일명 : 문자열(100)
    reg_date = db.Column(db.DateTime, nullable=False, default=datetime.now)         # 등록일 : DateTime, 기본갑 : 현재 시간
    img_url = db.Column(db.String(200))                                              # 원본 url : 문자열(200) (AWS S3에 저장되는 원본 이미지의 URL)
    thum_url = db.Column(db.String(200))                                             # 썸네일 url : 문자열(200) (AWS S3에 저장되는 썸네일 이미지의 URL)
    img_w = db.Column(db.Integer)                                                    # 이미지 너비 : 정수형
    img_h = db.Column(db.Integer)                                                    # 이미지 높이 : 정수형
    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), nullable=False)   # 사용자 번호 : 정수형, 외래키(사용자 테이블의 사용자 번호)

    def __init__(self, filename, img_url, thum_url, img_w, img_h, user_no):
        self.filename = filename
        self.img_url = img_url
        self.thum_url = thum_url
        self.img_w = img_w
        self.img_h = img_h
        self.user_no = user_no

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}

# 좋아요 테이블
class Likes(db.Model):
    __tablename__ = 'likes'     # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}   # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)    # 사용자 번호 : 정수형, 외래키(사용자 테이블의 사용자 번호), 기본키
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), primary_key=True)     # 이미지 번호 : 정수형, 외래키(이미지 테이블의 이미지 번호), 기본키

    images = db.relationship('Image', backref='liked')      # 이미지 테이블과 관계 생성 (Image(클래스이름) 참조, backref : 이미지 테이블에서 참조하는 이름)

    def __init__(self, user_no, img_no):
        self.user_no = user_no
        self.img_no = img_no

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if (select_cols is None) or (x.name in select_cols)}

# 대분류 테이블
class Major(db.Model):
    __tablename__ = 'major'     # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}   # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    major_no = db.Column(db.Integer, primary_key=True, autoincrement=True)      # 대분류 번호 : 정수형, 기본키, 자동증가
    c_major = db.Column(db.String(20), nullable=False)                          # 대분류 이름 : 문자열(20)

    cate = db.relationship('Category', backref="major")     # 분류 테이블과 관계 생성 (Category(클래스이름) 참조, backref : 분류 테이블에서 참조하는 이름)

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}

# 중분류 테이블
class Middle(db.Model):
    __tablename__ = 'middle'    # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}   # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    middle_no = db.Column(db.Integer, primary_key=True, autoincrement=True)     # 중분류 번호 : 정수형, 기본키, 자동증가
    c_middle = db.Column(db.String(20), nullable=False)                         # 중분류 이름 : 문자열(20)

    cate = db.relationship('Category', backref="middle")    # 분류 테이블과 관계 생성 (Category(클래스이름) 참조, backref : 분류 테이블에서 참조하는 이름)

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}

# 추천 이미지 테이블
class R_image(db.Model):
    __tablename__ = 'recommendations'   # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}    # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    no = db.Column(db.Integer, primary_key=True, autoincrement=True)   # 추천 번호 : 정수형, 기본키, 자동 증가
    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'))      # 사용자 번호 : 정수형, 외래키(사용자 테이블의 사용자 번호)
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'))       # 이미지 번호 : 정수형, 외래키(이미지 테이블의 이미지 번호)

    image = db.relationship('Image', backref='recommend')  # 이미지 테이블과 관계 생성 (Image(클래스이름) 참조, backref : 이미지 테이블에서 참조하는 이름)

    def __init__(self, user_no, img_no):
        self.user_no = user_no
        self.img_no = img_no

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}

# 인식된 태그 테이블
class Rec_tag(db.Model):
    __tablename__ = 'recognized_tag'    # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}   # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    no = db.Column(db.Integer, primary_key=True, autoincrement=True)                # 번호 : 정수형, 기본키, 자동증가
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), nullable=False)   # 이미지 번호 : 정수형, 외래키(이미지 테이블의 이미지 번호 참조)
    tag_no = db.Column(db.Integer, db.ForeignKey('tag.tag_no'), nullable=False)     # 태그 번호 : 정수형, 외래키(태그 테이블의 태그 번호 참조)
    x_1 = db.Column(db.Integer)                                                 # 인식된 태그 x1 좌표 : 정수형
    y_1 = db.Column(db.Integer)                                                 # 인식된 태그 y1 좌표 : 정수형
    x_2 = db.Column(db.Integer)                                                 # 인식된 태그 x2 좌표 : 정수형
    y_2 = db.Column(db.Integer)                                                 # 인식된 태그 y2 좌표 : 정수형

    image = db.relationship('Image', backref='rec_tags')        # 이미지 테이블과 관계 생성 (Image(클래스이름) 참조, backref : 이미지 테이블에서 참조하는 이름)
    tag = db.relationship('Tag', backref='rec_tags')            # 태그 테이블과 관계 생성 (Tag(클래스이름) 참조, backref : 태그 테이블에서 참조하는 이름)

    def __init__(self, img_no, tag_no, x_1, y_1, x_2, y_2):
        self.img_no = img_no
        self.tag_no = tag_no
        self.x_1 = x_1
        self.y_1 = y_1
        self.x_2 = x_2
        self.y_2 = y_2

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}

# 태그 테이블
class Tag(db.Model):
    __tablename__ = 'tag'    # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}   # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    tag_no = db.Column(db.Integer, primary_key=True, autoincrement=True)                # 태그 번호 : 정수형, 기본키, 자동증가
    cate_no = db.Column(db.Integer, db.ForeignKey('category.cate_no'), nullable=False)  # 분류 번호 : 정수형, 외래키(분류 테이블의 분류 번호 참조)
    tag = db.Column(db.String(20), nullable=False)                                      # 태그 이름 : 문자열(20)
    tag_han = db.Column(db.String(20), nullable=False)                                  # 태그 이름(한글) : 문자열(20)

   # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}

# 태그별 선호도 테이블
class Tag_pf(db.Model):
    __tablename__ = "tag_preference"    # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}    # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)    # 사용자 번호 : 정수형, 외래키(사용자 테이블의 사용자 번호 참조), 기본키
    tag_no = db.Column(db.Integer, db.ForeignKey('tag.tag_no'), primary_key=True)       # 태그 번호 : 정수형, 외래키(태그 테이블의 태그 번호 참조), 기본키
    preference = db.Column(db.Float, default=0)                                         # 선호도 : 실수형, 기본값 : 0

    def __init__(self, user_no, tag_no, preference):
        self.user_no = user_no
        self.tag_no = tag_no
        self.preference = preference

    def __init__(self, user_no, tag_no, preference):
        self.user_no = user_no
        self.tag_no = tag_no
        self.preference = preference

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}


# 사용자 테이블
class User(db.Model):
    __tablename__ = 'user'      # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}   # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    user_no = db.Column(db.Integer, primary_key=True, autoincrement=True)   # 사용자 번호 : 정수형, 기본키, 자동증가
    user_id = db.Column(db.String(20), nullable=False)                      # 사용자 ID : 문자열(20)
    user_pw = db.Column(db.String(20), nullable=False)                      # 사용자 PW : 문자열(20)

    images = db.relationship('Image', backref='user')       # 이미지 테이블과 관계 생성 (Image(클래스이름) 참조, backref : 이미지 테이블에서 참조하는 이름)
    likes = db.relationship('Likes', backref='user')        # 좋아요 테이블과 관계 생성 (Likes(클래스이름) 참조, backref : 좋아요 테이블에서 참조하는 이름)
    clicks = db.relationship('Click_data', backref='user')  # 클릭 데이터 테이블과 관계 생성 (Click_data(클래스이름) 참조, backref : 클릭 데이터 테이블에서 참조하는 이름)

    def __init__(self, user_id, user_pw):
        self.user_id = user_id
        self.user_pw = user_pw

    # 속성을 문자열로 반환할 경우
    def __repr__(self):
        return 'user_no : %s, user_id : %s, pw : %s' % (self.user_no, self.user_id, self.user_pw)

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}


class R_Input_DataSet(db.Model):
    __tablename__ = 'r_input_dataset'  # MySQL 테이블 이름
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}  # utf8 인코딩을 위한 속성 ( 한글 데이터 입력을 위함 )

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)  # 분류 번호 : 정수형, 기본키, 자동 증가
    tag_no = db.Column(db.Integer, db.ForeignKey('major.major_no'), primary_key=True)       # 대분류 번호 : 정수형, 외래키(대분류 테이블의 대분류 번호 참조), Not null
    tag = db.Column(db.String, db.ForeignKey('tag.tag'))
    u_cnt = db.Column(db.Integer)
    l_cnt = db.Column(db.Integer)
    s_cnt_d = db.Column(db.Integer)
    s_cnt_w = db.Column(db.Integer)
    s_cnt_m = db.Column(db.Integer)
    r_cnt_d = db.Column(db.Integer)
    r_cnt_w = db.Column(db.Integer)
    r_cnt_m = db.Column(db.Integer)
    major_no = db.Column(db.Integer, db.ForeignKey('major.major_no'))
    middle_no = db.Column(db.Integer, db.ForeignKey('middle.middle_no'))  # 중분류 번호 : 정수형, 외래키(중분류 테이블의 대분류 번호 참조), Not null
    c_major = db.Column(db.Integer, db.ForeignKey('major.c_major'))
    c_middle = db.Column(db.Integer, db.ForeignKey('middle.c_middle'))

    # 속성을 딕셔너리 형태로 반환
    def as_dict(self, select_cols=None):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns if
                (select_cols is None) or (x.name in select_cols)}