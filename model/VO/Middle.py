from model import db

class Middle(db.Model):
    __tablename__ = 'middle'
    __table_args__ = {'mysql_collate': 'utf8_general_ci'}

    middle_no = db.Column(db.Integer, primary_key=True, autoincrement=True)
    c_middle = db.Column(db.String(20), nullable=False)

    def as_dict(self):
        return {x.name: getattr(self, x.name) for x in self.__table__.columns}