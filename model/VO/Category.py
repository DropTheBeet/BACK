from model import db

class Category(db.Model):
    __tablename__ = 'category'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    cate_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    major_no = db.Column(db.Integer, db.ForeignKey('major.major_no'), nullable=False)
    middle_no = db.Column(db.Integer, db.ForeignKey('middle.middle_no'), nullable=False)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}