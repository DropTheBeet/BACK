from sqlalchemy import and_, func, desc
from model.models import Image, Rec_tag, Likes, R_image, Click_data
from model.util import query2list

# 테스트 DAO
class testDAO:
    def __init__(self, database):
        self.db = database

    # 이미지 번호에 해당하는 이미지 데이터 조회
    def get_image_data(self, img_no):
        img = Image.query.filter_by(img_no=img_no).first()

        img_data = img.as_dict(['img_no', 'user_no', 'filename'])

        print(img.rec_tags)

        rec_tags = []
        for rt in img.rec_tags:
            d = rt.as_dict()
            d['tag'] = rt.tag.tag
            rec_tags.append(d)

        img_data['reg_tags'] = rec_tags

        return img_data
        # {'img_no': 이미지 번호,
        #   'filename': 파일명,
        #   'user_no': 사용자 번호,
        #   'reg_tags': [{'no': Rec_tag 번호,
        #                   'img_no': 이미지 번호,
        #                   'tag_no': 태그 번호,
        #                   'x_1': x_1 좌표,
        #                   'y_1': y_1 좌표,
        #                   'x_2': x_2 좌표,
        #                   'y_2': y_2 좌표,
        #                   'tag': 태그 이름 }, ..., ]}

    # 모든 이미지 번호 조회
    def get_img_no_by_all(self):
        img_no_list = self.db.session.query(Image.img_no).all()

        return img_no_list          # [ (img_no, ), ... , ] 리스트안에 튜플 형식



