from model import db

class R_image(db.Model):
    __tablename__ = 'recommendations'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), primary_key=True)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}