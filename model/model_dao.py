import pandas as pd
from sqlalchemy import and_, not_
from model.models import R_Input_DataSet, R_image, Tag, Image, Tag_pf, User
from recommend import RecModel
from tqdm import tqdm


# 모델 DAO
class ModelDAO:
    # 각각의 값에 가중치 부여 (이 가중치는 계층화 분석과정인 AHP(Analytic Hierarchy Process에 의해 구한 값임))
    weights = {'upload_count': 0.6714,              # 업로드 빈도 가중치
               'like_count': 0.0842,                # 좋아요 빈도 가중치
               'search_click_cnt_month': 0.2046,    # 검색 클릭 빈도 가중치
               'rec_click_cnt_month': 0.0398}       # 추천 클릭 빈도 가중치

    def __init__(self, database):
        self.db = database

    def set_model(self, exc_tags=None):     # exc_tags : 모델에 반영할 데이터 중 제외할 태그 리스트
        input_user_data = R_Input_DataSet.query.all()  # 사용자별 선호도 계산에 반영될 데이터
        tag_data = Tag.query.all()  # 태그 데이터
        rec_tag_data = Image.query.all()  # 이미지별 인식된 태그를 추출하기 위한 이미지 데이터

        # 제외할 태그 리스트가 있을 경우
        if exc_tags is not None:
            input_user_data = R_Input_DataSet.query.filter(not_(R_Input_DataSet.tag_no.in_(exc_tags))).all()
            tag_data = Tag.query.filter(not_(R_Input_DataSet.tag_no.in_(exc_tags))).all()

        self.set_user_data(input_user_data)  # 사용자별 선호도 계산을 위한 데이터 세팅
        self.set_tag_data(tag_data)  # 태그 데이터 세팅
        self.set_recognized_tag_data(rec_tag_data, exc_tags)  # 이미지별 인식된 태그 데이터 세팅

        prefer_df = self.get_preferences_to_df()            # 선호도 데이터 계산
        self.rec_model = RecModel(self.user_df, prefer_df)  # 추천 모델 세팅

    def set_user_data(self, input_data):
        # 사용자별 선호도 계산을 위한 데이터 : 사용자 번호, 태그 번호, 태그 이름, 업로드 빈도, 좋아요 빈도, 검색 클릭 빈도(일, 주, 월), 추천 클릭 빈도(일, 주, 월),
        #                                대분류 번호, 중분류 번호, 대분류 이름, 중분류 이름
        userdatas = pd.DataFrame(columns=['user_no', 'tag_no', 'tag', 'upload_count', 'like_count',
                                   'search_click_cnt_day',  'search_click_cnt_week',
                                   'search_click_cnt_month', 'rec_click_cnt_day',
                                   'rec_click_cnt_week', 'rec_click_cnt_month',
                                   'major_no', 'middle_no', 'major', 'middle'])

        for i, data in enumerate(tqdm(input_data, desc="set_user_data")):
            userdatas.loc[i] = [data.user_no, data.tag_no, data.tag, data.u_cnt,
                         data.l_cnt, data.s_cnt_d, data.s_cnt_w, data.s_cnt_m,
                         data.r_cnt_d, data.r_cnt_w, data.r_cnt_m, data.major_no,
                         data.middle_no, data.c_major, data.c_middle]

        # 불필요한 컬럼 제거
        userdatas = userdatas.loc[:, ["user_no",
                                      "tag_no",
                                      "tag",
                                      "upload_count",
                                      "like_count",
                                      "search_click_cnt_month",
                                      "rec_click_cnt_month",
                                      "middle"]]
        # object형 데이터 int로 변환해주기
        userdatas[['user_no',
                   'tag_no',
                   'upload_count',
                   'like_count',
                   'search_click_cnt_month',
                   'rec_click_cnt_month']] = userdatas[['user_no',
                                                        'tag_no',
                                                        'upload_count',
                                                        'like_count',
                                                        'search_click_cnt_month',
                                                        'rec_click_cnt_month']].apply(pd.to_numeric,
                                                                                      errors="ignore")

        self.user_df = userdatas

    def set_tag_data(self, input_data):
        tags = pd.DataFrame(columns=['tag_no', 'tag'])

        for i, data in enumerate(tqdm(input_data, desc="set_tag_data")):
            tags.loc[i] = [data.tag_no, data.tag]

        self.tag_df =tags

    def set_recognized_tag_data(self, input_data, exc_tags=None):
        df = pd.DataFrame(columns=['image_no', 'user_no', 'tag_no'])

        i = 0
        for data in tqdm(input_data, desc="set_recognized_tag_data"):
            for rec_tag in data.rec_tags:
                if (exc_tags is not None) and (rec_tag.tag_no in exc_tags):
                    continue
                df.loc[i] = [data.img_no, data.user_no, rec_tag.tag_no]
                i = i + 1

        self.rectag_df = df

    # 사용자별 선호도 갱신
    def update_tag_preferences(self, weights=None):     # weights = 가중치
        if weights is not None:
            self.weights = weights

        preferences = self.get_new_preferences()    # 선호도 계산

        for i, row in tqdm(preferences.iterrows(), desc="update_tag_preferences"):
            u_no = int(row['user_no'])
            t_no = int(row['tag_no'])
            prefer = float(row['preference'])
            pf = Tag_pf(u_no, t_no, prefer)
            data = Tag_pf.query.filter_by(user_no=u_no, tag_no=t_no).first()    # 기존 사용자별 선호도 테이블을 조회
            if data is None:                        # 조회한 데이터가 없을 경우
                self.db.session.add(pf)             # INSERT
            else:                                   # 데이터가 있을 경우 기존 선호도를 갱신
                self.db.session.query(Tag_pf)\
                    .filter(and_(Tag_pf.user_no == u_no, Tag_pf.tag_no == t_no))\
                    .update({'preference': prefer})
        self.db.session.commit()    # COMMIT

    # 새로운 선호도 데이터 생성
    def get_new_preferences(self):
        w = self.weights        # 가중치

        df = self.user_df       # 선호도 계산을 위한 사용자 데이터
        df[[*w.keys()]] *= pd.Series(w)  # Series 형태로 변환하여 각각의 행에 곱해주는 작업

        # 각각의 값 더하여 선호도 컬럼 새로 만들어주기
        df2 = (df["upload_count"] +
               df["like_count"] +
               df["search_click_cnt_month"] +
               df["rec_click_cnt_month"])

        preferences = pd.concat([df, df2], axis=1)  # 새로 만들어준 선호도 컬럼 기존 DataFrame에 결합하기

        # 새로 만든 DataFrame에 필요없는 컬럼 제거
        preferences.drop(
            ['tag', 'middle', 'upload_count', 'like_count', 'search_click_cnt_month', 'rec_click_cnt_month'],
            axis='columns', inplace=True)

        # 새로만든 컬럼 이름 지정후 확인
        preferences.rename(columns={0: "preference"}, inplace=True)
        preferences[['user_no', 'tag_no']].apply(pd.to_numeric, errors="ignore")

        return preferences

    # 사용자별 선호도 데이터를 데이터프레임으로 변화하여 반환
    def get_preferences_to_df(self):
        preferences = Tag_pf.query.all()        # 사용자별 선호도 데이터 조회
        prefer_df = pd.DataFrame(columns=['user_no', 'tag_no', 'preference'])

        for i, pf in enumerate(tqdm(preferences, desc="get_preferences_to_df")):
            prefer_df.loc[i] = [pf.user_no, pf.tag_no, pf.preference]

        prefer_df2 = prefer_df.astype({'user_no':'int', 'tag_no':'int'})

        return prefer_df2

    # 추천 이미지 테이블 세팅
    def set_recommend_images(self):

        users = User.query.all()                    # 사용자 데이터 정보 조회

        for u in users:
            print("user_no[{}] 추천 이미지 세팅...".format(u.user_no))
            cur_r_imgs = R_image.query.filter_by(user_no=u.user_no).all()   # 사용자 번호에 해당하는 추천 이미지 조회
            if cur_r_imgs is not None:      # 조회한 이미지가 있을 경우
                self.db.session.query(R_image).filter(R_image.user_no == u.user_no).delete()    # 해당 데이터 삭제
            _r_imgs = self.rec_model.get_recommend_images(u.user_no, self.tag_df, self.rectag_df)  # 추천 모델을 통해 추천 이미지 생성
            for i, img in enumerate(tqdm(_r_imgs, desc="user_no[{}] insert_rec_image".format(u.user_no))):
                i_no = int(img[0])
                print("{}_ u_no : {}, i_no : {}".format(i, u.user_no, i_no))
                rec_img = R_image(u.user_no, i_no)  # 추천 이미지 데이터 생성
                self.db.session.add(rec_img)        # INSERT
        self.db.session.commit()    # COMMIT
