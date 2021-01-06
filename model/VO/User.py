from model import db


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
