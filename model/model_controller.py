import pandas as pd
from sqlalchemy import and_, not_
from model.models import R_Input_DataSet, R_image, Tag, Image, Tag_pf, User, Rec_tag_importance
from recommend import RecModel
from tqdm import tqdm
import numpy as np
from functools import reduce
import time
import threading
from threading import Thread

# 모델 DAO
class ModelController(Thread):
    user_no = None
    # 각각의 값에 가중치 부여 (이 가중치는 계층화 분석과정인 AHP(Analytic Hierarchy Process에 의해 구한 값임))
    weights = {'u_cnt': 0.6714,  # 업로드 빈도 가중치
               'l_cnt': 0.0842,  # 좋아요 빈도 가중치
               's_cnt_m': 0.2046,  # 검색 클릭 빈도 가중치
               'r_cnt_m': 0.0398}  # 추천 클릭 빈도 가중치

    def __init__(self, dao):
        Thread.__init__(self)
        self.model_dao = dao

    def set_input_data(self, exc_tags=None):     # exc_tags : 모델에 반영할 데이터 중 제외할 태그 리스트
        self.user_df = self.model_dao.get_user_data()  # 사용자별 선호도 계산을 위한 데이터 세팅
        self.tag_df = self.model_dao.get_tag_data()  # 태그 데이터 세팅
        self.rectag_df = self.model_dao.get_recognized_tag_data(exc_tags) # 이미지별 인식된 태그 데이터 세팅

    def set_model(self):
        prefer_df = self.model_dao.get_preferences_to_df()  # 선호도 데이터 계산
        self.rec_model = RecModel(self.user_df, prefer_df)  # 추천 모델 세팅

    # 사용자별 선호도 갱신
    def update_tag_preferences(self, weights=None, user_no=None):     # weights = 가중치
        if weights is not None:
            self.weights = weights

        preferences = self.get_new_preferences(user_no=user_no)    # 선호도 계산

        for i, row in tqdm(preferences.iterrows(), desc="update_tag_preferences"):
            u_no = int(row['user_no'])
            t_no = int(row['tag_no'])
            prefer = float(row['preference'])
            self.model_dao.insert_tag_pf(u_no, t_no, prefer)

    # 새로운 선호도 데이터 생성
    def get_new_preferences(self, user_no=None):
        print("get_new_preferences...")
        start = time.time()
        w = self.weights        # 가중치

        df = self.user_df  # 선호도 계산을 위한 사용자 데이터

        if user_no:
            df = self.model_dao.get_user_data(user_no)  # 선호도 계산을 위한 사용자 데이터

        df[[*w.keys()]] *= pd.Series(w)  # Series 형태로 변환하여 각각의 행에 곱해주는 작업

        # 각각의 값 더하여 선호도 컬럼 새로 만들어주기
        df2 = (df["u_cnt"] +
               df["l_cnt"] +
               df["s_cnt_m"] +
               df["r_cnt_m"])

        preferences = pd.concat([df, df2], axis=1)  # 새로 만들어준 선호도 컬럼 기존 DataFrame에 결합하기

        # 새로 만든 DataFrame에 필요없는 컬럼 제거
        preferences.drop(
            ['tag', 'c_middle', 'u_cnt', 'l_cnt', 's_cnt_m', 'r_cnt_m'],
            axis='columns', inplace=True)

        # 새로만든 컬럼 이름 지정후 확인
        preferences.rename(columns={0: "preference"}, inplace=True)
        preferences[['user_no', 'tag_no']].apply(pd.to_numeric, errors="ignore")

        end = time.time()
        print("get_new_preferences...END ::", (end - start))
        return preferences

    # 추천 이미지 테이블 세팅
    def set_recommend_images(self):

        users = User.query.all()                    # 사용자 데이터 정보 조회

        for u in users:
            print("user_no[{}] 추천 이미지 세팅...".format(u.user_no))
            cur_r_imgs = self.model_dao.get_recom_imgs_by_user(u.user_no)  # 사용자 번호에 해당하는 추천 이미지 조회
            if cur_r_imgs is not None:      # 조회한 이미지가 있을 경우
                self.model_dao.delete_recom_imgs_by_user(u.user_no)    # 해당 데이터 삭제
            _r_imgs = self.rec_model.get_recommend_images(u.user_no, self.tag_df, self.rectag_df)  # 추천 모델을 통해 추천 이미지 생성
            for i, img in enumerate(tqdm(_r_imgs, desc="user_no[{}] insert_rec_image".format(u.user_no))):
                i_no = int(img[0])
                print("{}_ u_no : {}, i_no : {}".format(i, u.user_no, i_no))
                self.model_dao.insert_recom_img(u.user_no, i_no)

    def set_recom_img_by_user(self, user_no):
        self.update_tag_preferences(user_no=user_no)

        prefer_df = self.model_dao.get_preferences_to_df()
        self.rec_model.set_prefer(prefer_df)

        print("user_no[{}] 추천 이미지 세팅...".format(user_no))
        cur_r_imgs = self.model_dao.get_recom_imgs_by_user(user_no) # 사용자 번호에 해당하는 추천 이미지 조회
        if cur_r_imgs is not None:  # 조회한 이미지가 있을 경우
            self.model_dao.delete_recom_imgs_by_user(user_no)  # 해당 데이터 삭제
        _r_imgs = self.rec_model.get_recommend_images(user_no, self.tag_df, self.rectag_df)  # 추천 모델을 통해 추천 이미지 생성
        for i, img in enumerate(tqdm(_r_imgs, desc="user_no[{}] insert_rec_image".format(user_no))):
            i_no = int(img[0])
            print("{}_ u_no : {}, i_no : {}".format(i, user_no, i_no))
            self.model_dao.insert_recom_img(user_no, i_no)

    # def set_user_no(self, no):
    #     self.user_no = no
    #
    # def run(self):
    #     self.set_recom_img()

    def set_recom_img(self, user_no):
        print("set_recom_img...")
        if user_no:
            self.set_recom_img_by_user(user_no)
        else:
            self.set_recommend_images()
        print("set_recom_img...END")