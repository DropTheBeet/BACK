from sqlalchemy import and_, func, desc
from model.models import Image, User, Rec_tag, Likes, Tag
from model.util import query2list


class ImageDAO:
    def __init__(self, database):
        self.db = database

    def get_image_list_by_user(self, user_no):
        _images = Image.query.filter_by(user_no=user_no).all()

        if _images is None:
            return None

        result = query2list(_images, ['img_no', 'thum_url', 'reg_date'])

        return result

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

        if user_no:
            final_query = self.db.session.query(Image) \
                .filter(and_(Image.img_no.in_(second_query), Image.user_no == user_no))

            _images = final_query.all()

            result = query2list(_images, ['img_no', 'thum_url', 'reg_date'])

            return result
        else:
            final_query = self.db.session.query(Image) \
                .filter(Image.img_no.in_(second_query))

            _images = final_query.all()

            result = query2list(_images, ['img_no', 'thum_url', 'reg_date'])

            return result

    def get_like_image_list_by_user(self, user_no):
        liked_imgs = Likes.query.filter_by(user_no=user_no).all()

        return [img.images.as_dict(['img_no', 'thum_url', 'reg_date']) for img in liked_imgs]

    def get_image_detail(self, img_no, user_no):
        _image = Image.query.filter_by(img_no=img_no).first()

        likes = [l.img_no for l in _image.liked if l.user_no == user_no]

        like = True if len(likes) > 0 else False

        img_owner_thum = Image.query.filter_by(user_no=_image.user_no).order_by(desc(Image.reg_date)).first()
        img_owner_thum = img_owner_thum.thum_url

        result = _image.as_dict(['img_no', 'img_url', 'reg_date', 'filename'])

        result.update(_image.user.as_dict(['user_no', 'user_id']))

        result.update({'like': like, 'profile_thum': img_owner_thum})

        return result

    # return "이미지번호, 원본url, 등록일, 파일명, 작성자 번호, 작성자 id, 작성자최신썸네일, 좋아요 여부"

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
        except:
            print("INSERT_IMAGE 실패 :", img)
            return False

        return True

    def insert_rec_tag(self, img_no, tag_data):
        try:
            for rt in tag_data:
                t_no = Tag.query.filter_by(tag=rt['tag']).first().tag_no
                rec_tag = Rec_tag(img_no,
                                  rt['tag_no'],
                                  rt['width'],
                                  rt['height'],
                                  rt['point_x'],
                                  rt['point_y'])
                self.db.session.add(rec_tag)
            self.db.session.commit()
        except:
            print("INSERT_REC_TAG 실패 :", tag_data)
            return False

        return True

    def delete_image(self, img_no):
        try:
            Rec_tag.query.filter_by(img_no=img_no).delete()
            Image.query.filter_by(img_no=img_no).delete()
            self.db.session.commit()
        except:
            print("DELETE_IMAGE 실패 :", img_no)
            return False

        return True

    def like_or_unlike_by_user_img(self, img_no, user_no):
        _like = Likes.query.filter_by(img_no=img_no, user_no=user_no).first()
        print(_like.as_dict())

        if _like is None:
            return False
        else:
            return True

    def insert_like(self, img_no, user_no):
        _like = Likes(user_no, img_no)

        try:
            self.db.session.add(_like)
            self.db.session.commit()
        except:
            print("INSERT_LIKE 실패 : user_no = {}, img_no = {}".format(user_no, img_no))
            return False

        return True

    def delete_like(self, img_no, user_no):

        try:
            Likes.query.filter_by(user_no=user_no, img_no=img_no).delete()
            self.db.session.commit()
        except:
            print("DELETE_LIKE 실패 : user_no = {}, img_no = {}".format(user_no, img_no))
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
