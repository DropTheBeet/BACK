from sqlalchemy import text
from model.models import Tag, Rec_tag, Image, Likes


# 태그 DAO
class TagDAO:
    def __init__(self, database):
        self.db = database

    # 사용자가 업로드한 사진에 존재하는 태그 리스트 조회
    def get_tag_list_by_user(self, user_no):
        try:
            # SELECT * FROM image WHERE user_no = ( 사용자 번호 )
            _images = Image.query.filter_by(user_no=user_no)
            # SELECT * FROM recognized_tag
            # WHERE img_no IN ( SELECT * FROM image WHERE user_no = ( 사용자 번호 ) ) GROUP BY tag_no
            _rec_tag = self.db.session.query(Rec_tag)\
                .filter(Rec_tag.img_no.in_([img.img_no for img in _images]))\
                .group_by(Rec_tag.tag_no).all()
        except Exception as e:
            # Error 발생할 경우
            print("GET_TAG_LIST_BY_USER 실패 : user_no = {}".format(user_no))
            print(e)
            return False

        tag_list = []

        for rt in _rec_tag:
            d = rt.tag.as_dict()                        # 태그 데이터 ( tag_no, cate_no, tag, tag_han )
            d.update(rt.tag.category.major.as_dict())   # 대분류 데이터 ( major_no, c_major )
            d.update(rt.tag.category.middle.as_dict())  # 중분류 데이터 ( middle_no, c_middle )
            tag_list.append(d)

        if len(tag_list) == 0:
            return None

        print(tag_list)
        return tag_list

    #대분류,중분류,태그

    # 전체 태그 리스트 조회
    def get_tag_list_all(self):
        try:
            _tags = Tag.query.all()     # 태그 데이터 조회
        except Exception as e:
            # Error 발생할 경우
            print("GET_TAG_LIST_ALL 실패 : ")
            print(e)
            return False
        tag_list = []
        for t in _tags:
            d = t.as_dict()                         # 태그 데이터 ( tag_no, cate_no, tag, tag_han )
            d.update(t.category.major.as_dict())    # 대분류 데이터 ( major_no, c_major )
            d.update(t.category.middle.as_dict())   # 중분류 데이터 ( middle_no, c_middle )
            tag_list.append(d)

        if len(tag_list) == 0:
            return None

        return tag_list

    # 사용자가 좋아요한 사진에 존재하는 태그 리스트 조회
    def get_like_tag_list_by_user(self, user_no):
        try:
            # SELECT * FROM likes WHERE user_no = ( 사용자 번호 )
            _likes = Likes.query.filter_by(user_no=user_no)
            # SELECT * FROM recognized_tag
            # WHERE img_no IN ( SELECT img_no FROM likes WHERE user_no = ( 사용자 번호 ) ) GROUP BY tag_no
            _rec_tag = self.db.session.query(Rec_tag) \
                .filter(Rec_tag.img_no.in_([like.images.img_no for like in _likes])) \
                .group_by(Rec_tag.tag_no).all()
        except Exception as e:
            # Error 발생할 경우
            print("GET_TAG_LIST_BY_USER 실패 : user_no = {}".format(user_no))
            print(e)
            return False

        tag_list = []

        for rt in _rec_tag:
            d = rt.tag.as_dict()  # 태그 데이터 ( tag_no, cate_no, tag, tag_han )
            d.update(rt.tag.category.major.as_dict())  # 대분류 데이터 ( major_no, c_major )
            d.update(rt.tag.category.middle.as_dict())  # 중분류 데이터 ( middle_no, c_middle )
            tag_list.append(d)

        if len(tag_list) == 0:
            return None

        print(tag_list)
        return tag_list

    # 대분류,중분류,태그