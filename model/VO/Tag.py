from model import db

class Tag(db.Model):
    __tablename__ = 'tag'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    tag_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cate_no = db.Column(db.Integer, db.ForeignKey('category.cate_no'), nullable=False)
    tag = db.Column(db.String(20), nullable=False)
    tag_han = db.Column(db.String(20), nullable=False)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}