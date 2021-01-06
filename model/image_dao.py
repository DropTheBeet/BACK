from sqlalchemy import text
from model.VO import Image
from util import query2list

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
        if (user_no):
            user_images = self.db.execute(text("""
    
    
                    """), {
                'user_no': user_no,
                'tag_no' : tag_list
            }).fetchall()

            return [{
                'img_no': user_image['img_no'],
                'thum_url': user_image['thum_url'],
                'reg_date': user_image['reg_date'],
            } for user_image in user_images]
        else:
            tag_images = self.db.execute(text("""


                    """), {
                'tag_no': tag_list
            }).fetchall()

            return [{
                'img_no': tag_image['img_no'],
                'thum_url': tag_image['thum_url'],
                'reg_date': tag_image['reg_date'],
            } for tag_image in tag_images]

    def get_like_image_list_by_id(self, user_no):
        user_like_images = self.db.execute(text("""


                """), {
            'user_no': user_no,
        }).fetchall()

        return [{
            'img_no': user_like_image['img_no'],
            'thum_url': user_like_image['thum_url'],
            'reg_date': user_like_image['reg_date'],
        } for user_like_image in user_like_images]


    def get_image_detail(self, img_no, user_no):
        original_image = self.db.execute(text("""
        
        """), {
            'img_no' : img_no,
            'user_no' : user_no
        }).fetchone()

        return {
                'img_no': original_image['img_no'],
                'img_url': original_image['img_url'],
                'reg_date': original_image['reg_date'],
            }

    # return,, "원본url, 사용자최신썸네일, id, 등록일, 좋아요 여부, 이미지, 번호    "


    def upload_image(self, thum_url,img_url, user_no, filename):
        return self.db.execute(text("""
        """), {
            'user_no' : user_no,
            'img_url' : img_url,
            'thum_url': thum_url,
            'filename' :filename
        }).rowcount

    def delete_image(self, img_no):
        return self.db.execute(text("""
            DELETE FROM 
        """), {
            'img_no' : img_no
        }).rowcount


    def like_or_unlike_by_id_img(self, img_no, user_no):
        like_1_unlike_0 = self.db.excute(text("""
        """), {
            'img_no': img_no,
            'user_no': user_no
        }).rowcount

        return like_1_unlike_0

    def insert_like(self, img_no, user_no):
        return self.db.execute(text("""
            INSERT INTO 
            

        """), {
            'user_no': user_no,
            'img_no' : img_no
        }).rowcount

    def delete_like(self, img_no, user_no):
        return self.db.execute(text("""
            DELETE FROM 
        """), {
            'user_no': user_no,
            'img_no' : img_no
        }).rowcount


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

