from sqlalchemy import text
from model.models import Tag, Rec_tag

class TagDAO:
    def __init__(self, database):
        self.db = database

    def get_tag_list_by_id(self, user_no):
        _rec_tag = Rec_tag.query.filter_by(img_no=user_no).group_by(Rec_tag.tag_no).all()

        tag_list = []

        for rt in _rec_tag:
            d = rt.tag.as_dict()
            d.update(rt.tag.category.major.as_dict())
            d.update(rt.tag.category.middle.as_dict())
            tag_list.append(d)

        if len(tag_list) == 0:
            return None

        return tag_list

    #대분류,중분류,태그


    def get_tag_list_all(self):
        _tags = Tag.query.all()
        tag_list = []
        for t in _tags:
            d = t.as_dict()
            d.update(t.category.major.as_dict())
            d.update(t.category.middle.as_dict())
            tag_list.append(d)

        if len(tag_list) == 0:
            return None

        return tag_list

    def get_tags_rating(self, user_no):
        tags_rating = self.db.execute(text("""

        """), {
            'user_no': user_no
        }).fetchall()


        return [{
            'tag_no': tag_rating['tag_no'],
            'rating': tag_rating['rating']
        } for tag_rating in tags_rating ]