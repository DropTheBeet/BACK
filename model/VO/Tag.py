from model import db

class Tag(db.Model):
    __tablename__ = 'tag'

    tag_no = db.Column(db.Integer, primary_key=True)
    cate_no = db.Column(db.Integer, db.ForeignKey('category.cate_no'), nullable=False)
    tag = db.Column(db.String(20), nullable=False)
    tag_han = db.Column(db.String(20), nullable=False)