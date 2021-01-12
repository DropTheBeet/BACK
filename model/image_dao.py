from sqlalchemy import and_, func, desc
from model.util import query2list


# 이미지 DAO
class ImageDAO:
    def __init__(self, database):
        self.db = database

    # 사용자가 업로드한 이미지 조회
    def get_image_list_by_user(self, user_no):
        try:
            _images = Image.query.filter_by(user_no=user_no).all()  # 사용자 번호에 해당하는 이미지 데이터 추출
        except Exception as e:
            # Error 발생할 경우
            print("GET_IMAGE_LIST_BY_USER 실패 :", user_no)
            print(e)
            return False

        # 추출된 이미지가 없을 경우
        if _images is None:
            return None

        result = query2list(_images,
                            ['img_no', 'thum_url', 'reg_date'])  # 추출된 이미지 데이터를 리스트로 변환(img_no, thum_url, reg_date 속성만)

        return result

    # 태그들을 포함한 이미지 조회 : 사용자가 선택한 태그들을 포함하는 이미지를 조회
    def get_image_list_by_tags(self, tag_list, user_no=None):

        # SELECT img_no, tag_no FROM recognized_tag WHERE tag_no IN ( 선택한 태그들 ) GROUP BY img_no, tag_no ORDER BY img_no
        first_query = self.db.session.query(Rec_tag.img_no, Rec_tag.tag_no) \
            .filter(Rec_tag.tag_no.in_(tag_list)) \
            .group_by(Rec_tag.img_no, Rec_tag.tag_no) \
            .order_by(Rec_tag.img_no).subquery()

        # SELECT img_no FROM first_query GROUP BY img_no HAVING count(tag_no) = (선택한 태그의 갯수)
        second_query = self.db.session.query(first_query.c.img_no) \
            .select_from(first_query) \
            .group_by(first_query.c.img_no) \
            .having(func.count(first_query.c.tag_no) == len(tag_list)).subquery()
        try:
            if user_no:  # 사용자가 업로드한 이미지 중에서 조회할 경우
                # SELECT * FROM image WHERE img_no IN ( second_query ) AND user_no = ( 사용자 번호 )
                final_query = self.db.session.query(Image) \
                    .filter(and_(Image.img_no.in_(second_query), Image.user_no == user_no))

                _images = final_query.all()

                result = query2list(_images, ['img_no', 'thum_url',
                                              'reg_date'])  # 추출된 이미지 데이터를 리스트로 변환(img_no, thum_url, reg_date 속성만)

                return result
            else:  # 전체 이미지 중에서 조회할 경우
                # SELECT * FROM image WHERE img_no IN ( second_query )
                final_query = self.db.session.query(Image) \
                    .filter(Image.img_no.in_(second_query))

                _images = final_query.all()

                result = query2list(_images, ['img_no', 'thum_url',
                                              'reg_date'])  # 추출된 이미지 데이터를 리스트로 변환(img_no, thum_url, reg_date 속성만)

                return result
        except Exception as e:
            # Error 발생
            print("GET_IMAGE_LIST_BY_TAGS 실패 : tag_list = {}, user_no = {}".format(tag_list, user_no))
            print(e)
            return False

    # 사용자의 추천 이미지 정보 조회
    def get_recommend_image_list_by_user(self, user_no):
        try:
            _r_imgs = R_image.query.filter_by(user_no=user_no).all()    # 사용자 번호에 해당하는 추천 이미지 조회
            result = []
            for img in _r_imgs:
                result.append(img.as_dict(['img_no', 'thum_url', 'reg_date']))
            return result           # 추출된 이미지 데이터를 리스트로 반환
                                    # [{'img_no' : img_no, 'thum_url' : thum_url, 'reg_date' : reg_date}, ..., ]
        except Exception as e:
            print("GET_RECOMMEND_IMAGE_LIST_BY_USER 실패 : user_no = {}".format(user_no))
            print(e)
            return False

    # 사용자의 좋아요한 이미지 조회
    def get_like_image_list_by_user(self, user_no):
        try:
            liked_imgs = Likes.query.filter_by(user_no=user_no).all()  # 사용자 번호에 해당하는 좋아요 데이터 추출
        except Exception as e:
            # Error 발생할 경우
            print("GET_LIKE_IMAGE_LIST_BY_USER 실패 : user_no = {}".format(user_no))
            print(e)
            return False

        return [img.images.as_dict(['img_no', 'thum_url', 'reg_date']) for img in
                liked_imgs]  # 추출된 좋아요 데이터에서 이미지를 참조하여 리스트로 반환(img_no, thum_url, reg_date 속성만)

    # 이미지 상세정보 조회
    def get_image_detail(self, img_no, user_no):
        try:
            _image = Image.query.filter_by(img_no=img_no).first()  # 이미지 번호에 해당하는 이미지 데이터를 추출
        except Exception as e:
            # Error 발생할 경우
            print("GET_IMAGE_DETAIL 이미지 데이터 불러오기 실패 : img_no = {}".format(img_no))
            print(e)
            return False

        _likes = [l.img_no for l in _image.liked if
                  l.user_no == user_no]  # 추출된 이미지 데이터에서 좋아요를 참조하여 사용자 번호와 일치하는 경우를 리스트로 만듬
        like = True if len(_likes) > 0 else False  # _likes의 요소 개수가 0 이상일 경우 좋아요 여부 True

        try:
            # 이미지 작성자의 썸네일 추출 ( 작성자의 최신 업로드 이미지 )
            img_owner_thum = Image.query.filter_by(user_no=_image.user_no).order_by(desc(Image.reg_date)).first()
        except Exception as e:
            # Error 발생할 경우
            print("GET_IMAGE_DETAIL 작성자 썸네일 불러오기 실패 : user_no = {}".format(user_no))
            print(e)
            return False

        img_owner_thum = img_owner_thum.thum_url  # 이미지 작성자의 썸네일 URL

        result = _image.as_dict(['img_no', 'img_url', 'reg_date', 'filename'])

        result.update(_image.user.as_dict(['user_no', 'user_id']))  # result에 작성자의 번호와 아이디를 추가

        result.update({'like': like, 'profile_thum': img_owner_thum})  # result에 사용자의 좋아요 여부와 작성자의 썸네일 추가

        return result  # return "이미지번호, 원본url, 등록일, 파일명, 작성자 번호, 작성자 id, 작성자최신썸네일, 좋아요 여부"

    # 이미지 업로드
    def insert_image(self, img):
        # 입력값 : { filename : filename,
        #           img_url : img_url,
        #           thum_url : thum_url,
        #           img_w : 이미지 너비,
        #           img_h : 이미지 높이,
        #           user_no : user_no,
        #           tag_data : [{
        #                   tag: "태그 이름"(영어),
        #                   width: "태그 너비",
        #                   height: "태그 높이",
        #                   point_x: "x 좌표",
        #                   point_y: "y 좌표"
        #                   }, ..., ]
        # 업로드할 이미지 데이터 생성 ( 파일명, 이미지 URL, 썸네일 URL, 이미지 너비, 이미지 높이, 사용자 번호 )
        upload_img = Image(img['filename'],
                           img['img_url'],
                           img['thum_url'],
                           img['img_w'],
                           img['img_h'],
                           img['user_no'])

        try:
            self.db.session.add(upload_img)  # INSERT
            self.db.session.commit()  # COMMIT

            # INSERT한 후에 생성된 이미지 번호 추출
            img_no = Image.query.filter_by(filename=img['filename']).first().img_no

            # 인식된 태그 데이터 삽입
            if not self.insert_rec_tag(img_no, img['tag_data']):
                # 태그 데이터 삽입 Error 발생할 경우
                return False
        except Exception as e:
            # Error 발생할 경우
            print("INSERT_IMAGE 실패 : img_data = {}".format(img))
            print(e)
            return False

        return True

    # 인식된 태그 삽입 : 이미지 업로드 시 이미지의 인식된 태그 데이터 저장
    def insert_rec_tag(self, img_no, tag_data):
        try:
            for rt in tag_data:
                # 삽입할 인식된 태그 데이터 생성
                rec_tag = Rec_tag(img_no,
                                  rt['t_no'],
                                  rt['width'],
                                  rt['height'],
                                  rt['point_x'],
                                  rt['point_y'])
                self.db.session.add(rec_tag)  # INSERT
            self.db.session.commit()  # COMMIT
        except Exception as e:
            # Error 발생할 경우
            print("INSERT_REC_TAG 실패 : tag_data = {}".format(tag_data))
            print(e)
            return False

        return True

    # 이미지 삭제
    def delete_image(self, img_no):
        try:
            self.db.session.query(Rec_tag).filter(
                Rec_tag.img_no == img_no).delete()  # recognized_tag 테이블의 이미지 번호에 해당하는 데이터를 DELETE
            self.db.session.query(Image).filter(Image.img_no == img_no).delete()  # image 테이블의 이미지 번호에 해당하는 데이터를 DELETE
            self.db.session.commit()  # COMMIT
        except Exception as e:
            # Error 발생할 경우
            print("DELETE_IMAGE 실패 : img_no = {}".format(img_no))
            print(e)
            return False

        return True

    # 인식된 태그 삭제 : 사용 안함
    def delete_rec_tag(self, img_no):
        try:
            rts = Rec_tag.query.filter_by(img_no=img_no).all()  # 이미지 번호에 해당하는 인식된 태그를 추출
            for rt in rts:
                self.db.session.delete(rt)  # DELETE
                self.db.session.commit()  # COMMIT
        except Exception as e:
            # Error 발생할 경우
            print("DELETE_REC_TAG 실패 : img_no = {}".format(img_no))
            print(e)
            return False

    # 이미지의 좋아요 여부 조회 : 사용자가 이미지를 좋아요한지 안한지 확인
    def like_or_unlike_by_user_img(self, img_no, user_no):
        try:
            _like = Likes.query.filter_by(img_no=img_no, user_no=user_no).first()  # 이미지번호와 사용자번호에 해당하는 좋아요 데이터를 추출
        except Exception as e:
            # Error 발생할 경우
            print("LIKE_OR_UNLIKE_BY_USER_IMG 실패 : img_no = {}, user_no = {}".format(img_no, user_no))
            print(e)
            return False

        if _like is None:  # 추출된 데이터가 없을 경우
            return False
        else:
            return True

    # 좋아요 삽입 : 사용자가 이미지를 좋아요했을 시
    def insert_like(self, user_no, img_no):
        _like = Likes(user_no, img_no)  # 좋아요 데이터 생성 ( 사용자 번호, 이미지 번호 )
        try:
            self.db.session.add(_like)  # INSERT
            self.db.session.commit()  # COMMIT
        except Exception as e:
            # Error 발생할 경우
            print("INSERT_LIKE 실패 : user_no = {}, img_no = {}".format(user_no, img_no))
            print(e)
            return False

        return True

    # 좋아요 삭제 : 사용자가 좋아요한 이미지에 대해 좋아요를 취소했을 시
    def delete_like(self, user_no, img_no):
        try:
            Likes.query.filter_by(user_no=user_no,
                                  img_no=img_no).delete()  # likes 테이블의 이미지 번호와 사용자 번호에 해당하는 데이터를 DELETE
            self.db.session.commit()  # COMMIT
        except Exception as e:
            # Error 발생할 경우
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
