from model import db

class Click_data(db.Model):
    __tablename__ = 'click_data'

    no = db.Column(db.Integer, primary_key=True)
    user_no = db.Column(db.Integer, db.ForeignKey('user.user_no'))
    img_no = db.Column(db.Integer, db.ForeignKey('image.img_no'), nullable=False)
    type = db.Column(db.Char, nullable=False)
    click_date = db.Column(db.DateTime, nullable=False, default=datetime.now)