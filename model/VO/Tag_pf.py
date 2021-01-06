from model import db

class Tag_pf(db.Model):

    __tablename__ = "tag_preference"
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'), primary_key=True)
    tag_no = db.Column(db.Integer, db.ForeignKey('tag.tag_no'), primary_key=True)
    preference = db.Column(db.Float, default=0)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}