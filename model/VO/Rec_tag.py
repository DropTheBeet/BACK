from BACK.model import db

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