from model import db

class Major(db.Model):
    __tablename__ = 'major'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    major_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_major = db.Column(db.String(20), nullable=False)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}