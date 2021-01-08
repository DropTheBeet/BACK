from sqlalchemy import and_, func, desc
from model.models import Image, User, Rec_tag, Likes, Tag
from model.util import query2list


class ImageDAO:
    def __init__(self, database):
        self.db = database

    # 사용자가 업로드한 이미지 조회
    def get_image_list_by_user(self, user_no):
        try:
            _images = Image.query.filter_by(user_no=user_no).all()
        except Exception as e:
            print("GET_IMAGE_LIST_BY_USER 실패 :", user_no)
            print(e)
            return False;
        if _images is None:
            return None

        result = query2list(_images, ['img_no', 'thum_url', 'reg_date'])

        return result

    # 태그들을 포함한 이미지 조회 : 사용자가 선택한 태그들을 포함하는 이미지를 조회
    def get_image_list_by_tags(self, tag_list, user_no=None):
        print("Search tags :", tag_list)
        first_query = self.db.session.query(Rec_tag.img_no, Rec_tag.tag_no) \
            .filter(Rec_tag.tag_no.in_(tag_list)) \
            .group_by(Rec_tag.img_no, Rec_tag.tag_no) \
            .order_by(Rec_tag.img_no).subquery()

        second_query = self.db.session.query(first_query.c.img_no) \
            .select_from(first_query) \
            .group_by(first_query.c.img_no) \
            .having(func.count(first_query.c.tag_no) == len(tag_list)).subquery()
        try:
            if user_no:     # 사용자가 업로드한 이미지 중에서 조회할 경우

                final_query = self.db.session.query(Image) \
                    .filter(and_(Image.img_no.in_(second_query), Image.user_no == user_no))

                _images = final_query.all()

                result = query2list(_images, ['img_no', 'thum_url', 'reg_date'])

                return result
            else:           # 전체 이미지 중에서 조회할 경우
                final_query = self.db.session.query(Image) \
                    .filter(Image.img_no.in_(second_query))

                _images = final_query.all()

                result = query2list(_images, ['img_no', 'thum_url', 'reg_date'])

                return result
        except Exception as e:
            print("GET_IMAGE_LIST_BY_TAGS 실패 : tag_list = {}, user_no = {}".format(tag_list, user_no))
            print(e)
            return False

    # 사용자의 좋아요한 이미지 조회
    def get_like_image_list_by_user(self, user_no):
        try:
            liked_imgs = Likes.query.filter_by(user_no=user_no).all()
        except Exception as e:
            print("GET_LIKE_IMAGE_LIST_BY_USER 실패 : user_no = {}".format(user_no))
            print(e)
            return False
        return [img.images.as_dict(['img_no', 'thum_url', 'reg_date']) for img in liked_imgs]

    # 이미지 상세정보 조회
    def get_image_detail(self, img_no, user_no):
        try:
            _image = Image.query.filter_by(img_no=img_no).first()
        except Exception as e:
            print("GET_IMAGE_DETAIL 이미지 데이터 불러오기 실패 : img_no = {}".format(img_no))
            print(e)
            return False


        likes = [l.img_no for l in _image.liked if l.user_no == user_no]

        like = True if len(likes) > 0 else False

        try:
            img_owner_thum = Image.query.filter_by(user_no=_image.user_no).order_by(desc(Image.reg_date)).first()
        except Exception as e:
            print("GET_IMAGE_DETAIL 작성자 썸네일 불러오기 실패 : user_no = {}".format(user_no))
            print(e)
            return False

        img_owner_thum = img_owner_thum.thum_url

        result = _image.as_dict(['img_no', 'img_url', 'reg_date', 'filename'])

        result.update(_image.user.as_dict(['user_no', 'user_id']))

        result.update({'like': like, 'profile_thum': img_owner_thum})

        return result                       # return "이미지번호, 원본url, 등록일, 파일명, 작성자 번호, 작성자 id, 작성자최신썸네일, 좋아요 여부"

    # 이미지 업로드
    def insert_image(self, img):
        upload_img = Image(img['filename'],
                           img['img_url'],
                           img['thum_url'],
                           img['img_w'],
                           img['img_h'],
                           img['user_no'])

        try:
            self.db.session.add(upload_img)
            self.db.session.commit()

            img_no = Image.query.filter_by(filename=img['filename']).first().img_no

            if not self.insert_rec_tag(img_no, img['tag_data']):
                return False
        except Exception as e:
            print("INSERT_IMAGE 실패 : img_data = {}".format(img))
            print(e)
            return False

        return True

    # 인식된 태그 삽입 : 이미지 업로드 시 이미지의 인식된 태그 데이터 저장
    def insert_rec_tag(self, img_no, tag_data):
        try:
            for rt in tag_data:
                t_no = Tag.query.filter_by(tag_han=rt['tag']).first().tag_no
                print(t_no)
                rec_tag = Rec_tag(img_no,
                                  t_no,
                                  rt['width'],
                                  rt['height'],
                                  rt['point_x'],
                                  rt['point_y'])
                self.db.session.add(rec_tag)
            self.db.session.commit()
        except Exception as e:
            print("INSERT_REC_TAG 실패 : tag_data = {}".format(tag_data))
            print(e)
            return False

        return True

    # 이미지 삭제
    def delete_image(self, img_no):
        print(img_no)
        try:
            print(type(img_no))
            self.db.session.query(Rec_tag).filter(Rec_tag.img_no == img_no).delete()
            self.db.session.query(Image).filter(Image.img_no == img_no).delete()
            self.db.session.commit()
        except Exception as e:
            print("DELETE_IMAGE 실패 : img_no = {}".format(img_no))
            print(e)
            return False

        return True

    # 인식된 태그 삭제 : 아직 사용 안함
    def delete_rec_tag(self, img_no):
        try:
            rts = Rec_tag.query.filter_by(img_no=img_no).all()
            for rt in rts:
                self.db.session.delete(rt)
                self.db.session.commit()
        except Exception as e:
            print("DELETE_REC_TAG 실패 : img_no = {}".format(img_no))
            print(e)
            return False

    # 이미지의 좋아요 여부 조회 : 사용자가 이미지를 좋아요한지 안한지 확인
    def like_or_unlike_by_user_img(self, img_no, user_no):
        try:
            _like = Likes.query.filter_by(img_no=img_no, user_no=user_no).first()
        except Exception as e:
            print("LIKE_OR_UNLIKE_BY_USER_IMG 실패 : img_no = {}, user_no = {}".format(img_no, user_no))
            print(e)
            return False

        if _like is None:
            return False
        else:
            return True

    # 좋아요 삽입 : 사용자가 이미지를 좋아요했을 시
    def insert_like(self, img_no, user_no):
        _like = Likes(user_no, img_no)

        try:
            self.db.session.add(_like)
            self.db.session.commit()
        except Exception as e:
            print("INSERT_LIKE 실패 : user_no = {}, img_no = {}".format(user_no, img_no))
            print(e)
            return False

        return True

    # 좋아요 삭제 : 사용자가 좋아요한 이미지에 대해 좋아요를 취소했을 시
    def delete_like(self, img_no, user_no):
        try:
            Likes.query.filter_by(user_no=user_no, img_no=img_no).delete()
            self.db.session.commit()
        except Exception as e:
            print("DELETE_LIKE 실패 : user_no = {}, img_no = {}".format(user_no, img_no))
            print(e)
            return False

        return True

    def get_image_info(self, recommended_image_no_by_tensor):
        recommended_images = self.db.execute(text("""


        """), {
            'img_no': recommended_image_no_by_tensor
        }).fetchall()

        return [{
            'img_no': recommended_image['img_no'],
            'thum_url': recommended_image['thum_url'],
            'reg_date': recommended_image['reg_date'],
        } for recommended_image in recommended_images]
