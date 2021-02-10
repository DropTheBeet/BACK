import pandas as pd
from sqlalchemy import and_, not_
from model.models import R_Input_DataSet, R_image, Tag, Image, Tag_pf, User, Rec_tag_importance
from recommend import RecModel
from tqdm import tqdm
import numpy as np
from functools import reduce
import time


# 모델 DAO
class ModelDAO:
    def __init__(self, database):
        self.db = database


    def get_user_data(self, user_no=None):
        print("set_user_data...")
        start = time.time()
        # 사용자별 선호도 계산을 위한 데이터 : 사용자 번호, 태그 번호, 태그 이름, 업로드 빈도, 좋아요 빈도, 검색 클릭 빈도(일, 주, 월), 추천 클릭 빈도(일, 주, 월),
        #                                대분류 번호, 중분류 번호, 대분류 이름, 중분류 이름

        if user_no:
            query = R_Input_DataSet.query.filter_by(user_no=user_no)
        else:
            query = R_Input_DataSet.query  # 사용자별 선호도 계산에 반영될 데이터

        userdatas = pd.read_sql(query.statement, query.session.bind)

        # 불필요한 컬럼 제거
        userdatas = userdatas.loc[:, ["user_no",
                                      "tag_no",
                                      "tag",
                                      "u_cnt",
                                      "l_cnt",
                                      "s_cnt_m",
                                      "r_cnt_m",
                                      "c_middle"]]
        # object형 데이터 int로 변환해주기
        userdatas[['user_no',
                   'tag_no',
                   'u_cnt',
                   'l_cnt',
                   's_cnt_m',
                   'r_cnt_m']] = userdatas[['user_no',
                                            'tag_no',
                                            'u_cnt',
                                            'l_cnt',
                                            's_cnt_m',
                                            'r_cnt_m']].apply(pd.to_numeric,
                                                              errors="ignore")
        end = time.time()
        print("set_user_data...END ::", (end - start))

        return userdatas

    def get_tag_data(self):
        print("get_tag_data...")
        start = time.time()
        query = Tag.query  # 태그 데이터

        tags = pd.read_sql(query.statement, query.session.bind)

        end = time.time()
        print("get_tag_data...END ::", (end - start))

        return tags

    def get_recognized_tag_data(self, exc_tags=None):
        print("get_recognized_tag_data...")
        start = time.time()
        # 이미지별 인식된 태그를 추출하기 위한 이미지 데이터
        query = self.db.session.query(Image.img_no, Image.user_no, Rec_tag_importance.tag_no, Rec_tag_importance.importance )\
                            .join(Rec_tag_importance, Rec_tag_importance.img_no == Image.img_no)

        df = pd.read_sql(query.statement, query.session.bind)

        # object형 데이터 int로 변환해주기
        df[['user_no', 'tag_no', 'img_no']] = df[['user_no', 'tag_no', 'img_no']].apply(pd.to_numeric, errors="ignore")
        rec_tag_df = df.astype({'user_no': 'int', 'tag_no': 'int', 'img_no': 'int'})

        # object형 데이터 int로 변환해주기
        rec_tag_df[['user_no', 'tag_no', 'img_no']] = rec_tag_df[['user_no', 'tag_no', 'img_no']].apply(
            pd.to_numeric,
            errors="ignore")

        # map - reduce 작업 (태그하나와 이미지 하나를 같은 벡터로 보고 펼쳐준 후,
        # 다시 합쳐 80개의 태그, 이미지를 하나의 벡터로 만드는 작업)
        def map_reduce(subset):
            tag_no = subset['tag_no']
            m = map(lambda x: np.eye(80)[x - 1], tag_no)

            r = reduce(lambda x, y: x + y, m)
            return r

        image_info = rec_tag_df.groupby("img_no").apply(map_reduce)

        info_list = np.array(image_info)

        image_info.to_csv('image_info.csv')
        img_no_df = pd.read_csv("image_info.csv", sep=",", encoding="CP949", header=None)
        img_no_df = img_no_df.rename(columns=img_no_df.iloc[0])
        # 조정후 필요없는 행 삭제
        img_no_df = img_no_df.drop(img_no_df.index[0])

        img_no_df['img_no'] = img_no_df['img_no'].apply(pd.to_numeric, errors="ignore")

        end = time.time()
        print("get_recognized_tag_data...END ::", (end - start))

        return list(zip(img_no_df['img_no'], info_list))

    # 사용자별 선호도 데이터를 데이터프레임으로 변화하여 반환
    def get_preferences_to_df(self):
        print("get_preferences_to_df...")
        start = time.time()
        query = Tag_pf.query  # 사용자별 선호도 데이터 조회
        prefer_df = pd.read_sql(query.statement, query.session.bind)

        prefer_df2 = prefer_df.astype({'user_no': 'int', 'tag_no': 'int'})
        prefer_df2[['user_no', 'tag_no']].apply(pd.to_numeric, errors="ignore")

        end = time.time()
        print("get_preferences_to_df...END ::", (end - start))
        return prefer_df2

    def get_recom_imgs_by_user(self, user_no):
        return R_image.query.filter_by(user_no=user_no).all()

    def delete_recom_imgs_by_user(self, user_no):
        self.db.session.query(R_image).filter(R_image.user_no == user_no).delete()

    def insert_recom_img(self, user_no, img_no):
        rec_img = R_image(user_no, img_no)  # 추천 이미지 데이터 생성
        self.db.session.add(rec_img)  # INSERT
        self.db.session.commit()

    def insert_tag_pf(self, user_no, tag_no, prefer):
        pf = Tag_pf(user_no, tag_no, prefer)
        data = Tag_pf.query.filter_by(user_no=user_no, tag_no=tag_no).first()  # 기존 사용자별 선호도 테이블을 조회
        if data is None:  # 조회한 데이터가 없을 경우
            self.db.session.add(pf)  # INSERT
        else:  # 데이터가 있을 경우 기존 선호도를 갱신
            self.db.session.query(Tag_pf) \
                .filter(and_(Tag_pf.user_no == user_no, Tag_pf.tag_no == tag_no)) \
                .update({'preference': prefer})
        self.db.session.commit()