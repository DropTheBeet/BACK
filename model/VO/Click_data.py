from model import db
from datetime import datetime

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