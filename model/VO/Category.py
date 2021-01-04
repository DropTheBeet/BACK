from model import db

class Category(db.Model):
    __tablename__ = 'category'

    cate_no = db.Column(db.Integer, primary_key=True)
    major_no = db.Column(db.Integer, db.ForeignKey('major.major_no'), nullable=False)
    middle_no = db.Column(db.Integer, db.ForeignKey('middle.middle_no'), nullable=False)