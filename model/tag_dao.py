from sqlalchemy import text
from model.models import Tag, Rec_tag

class TagDAO:
    def __init__(self, database):
        self.db = database

    def get_tag_list_by_user(self, user_no):
        try:
            _rec_tag = Rec_tag.query.filter_by(img_no=user_no).group_by(Rec_tag.tag_no).all()
        except Exception as e:
            print("GET_TAG_LIST_BY_USER 실패 : user_no = {}".format(user_no))
            print(e)
            return False

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
        try:
            _tags = Tag.query.all()
        except Exception as e:
            print("GET_TAG_LIST_ALL 실패 : ")
            print(e)
            return False
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