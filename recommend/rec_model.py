import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm


# 추천 모델
class RecModel:
    # SIG_LEVEL은 최소 신뢰도(공통 태그 선호도의 갯수)
    SIG_LEVEL = 5
    # MIN_RATINGS는 최소 선호도 점수를 뜻함
    MIN_RATINGS = 15

    def __init__(self, user_data, preferences):
        self.user_data = user_data
        self.tag_mean = preferences.groupby(['tag_no'])['preference'].mean()

        # 데이터셋 train과 test로 분리
        x = preferences.copy()
        y = preferences['user_no']

        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, stratify=y)

        self.set_rating(x_train)
        self.set_best_neighbor_size(x_test)

    def get_recommend_images(self, user_no, taglist, rec_taglist):

        n_size = self.best_neighbor_size[0]  # 최적의 neighbor_size

        recom_tag = self.recom_tag(user_no=user_no, n_items=10, tags=taglist, neighbor_size=n_size)
        recommend_list = recom_tag

        print(recommend_list.index)
        recom_list = list(recommend_list.index)

        # image no가 있는 데이터셋 불러오기
        rec_tag_df = rec_taglist

        # object형 데이터 int로 변환해주기
        rec_tag_df[['user_no', 'tag_no', 'image_no']] = rec_tag_df[['user_no', 'tag_no', 'image_no']].apply(
            pd.to_numeric,
            errors="ignore")

        # map - reduce 작업 (태그하나와 이미지 하나를 같은 벡터로 보고 펼쳐준 후,
        # 다시 합쳐 80개의 태그, 이미지를 하나의 벡터로 만드는 작업)
        def map_reduce(subset):
            tag_no = subset['tag_no']
            m = map(lambda x: np.eye(80)[x - 1], tag_no)
            from functools import reduce
            r = reduce(lambda x, y: x + y, m)
            return r

        image_info = rec_tag_df.groupby("image_no").apply(map_reduce)

        print("image_info : ", image_info)

        # 리스트에 담긴 값은 추천된 10개의 태그를 하나의 벡터로 만들어놓은 값이다.
        recommend_image = np.zeros(80, dtype=float)
        for tag_no in recom_list:
            t_no = int(tag_no)
            recommend_image[t_no - 1] = 1.

        info_list = np.array(image_info)
        print("info_list : ", info_list)
        recom_list = recommend_image  # 추천 태그 리스트 벡터
        print("recom_list : ", recom_list)
        return self.get_best_imgs(info_list, recom_list)

    def get_best_imgs(self, info_list, recom_list, num=30):
        # 상위 30개 이미지 번호와 유사도
        best_img_sims = [[-1, -1], ]

        for img_no, image_vector in tqdm(enumerate(info_list), desc="get_best_imgs"):
            # 유사도 계산
            cos_sim = self.compute_cos_similarity(recom_list, image_vector)

            for i in range(0, len(best_img_sims)):
                if cos_sim > best_img_sims[i][1]:  # 계산된 유사도를 리스트와 비교
                    if len(best_img_sims) < num:  # 리스트의 요소가 num 미만일 경우
                        best_img_sims.insert(i, [img_no, cos_sim])  # 해당 위치에 삽입
                        break
                    else:  # 그렇지 않을 경우
                        best_img_sims.insert(i, [img_no, cos_sim])  # 해당위치에 삽입 후
                        del best_img_sims[-1]  # 맨 끝의 요소 삭제
                        break

        return best_img_sims

    def set_rating(self, x_train):
        rating_matrix = x_train.pivot_table(values='preference', index='user_no', columns='tag_no')

        pre_matrix = x_train.pivot(index='user_no', columns='tag_no', values='preference')  # 예측 행렬 생성

        rating_dummy = pre_matrix.copy().fillna(0)  # 결측치를 채운 더미 데이터 생성

        # train set을 코사인 유사도를 이용하여 유저간 유사도 구하기
        similarity = cosine_similarity(rating_dummy, rating_dummy)
        # 구한 유사도값 DataFrame화 하기
        self.user_similarity = pd.DataFrame(similarity, index=pre_matrix.index, columns=pre_matrix.index)

        # train 데이터의 user의 rating 평균과 태그의 평점편차 계산
        self.rating_mean = pre_matrix.mean(axis=1)
        self.rating_bias = (pre_matrix.T - self.rating_mean).T

        # 사용자별 공통 평가 목록 갯수 계산
        rating_binary1 = np.array((rating_matrix > 0).astype(float))
        rating_binary2 = rating_binary1.T
        cnts = np.dot(rating_binary1, rating_binary2)
        self.counts = pd.DataFrame(cnts, index=rating_matrix.index, columns=rating_matrix.index).fillna(0)

    def CF_knn_bias_sig(self, user_no, tag_no, neighbor_size=0):
        if tag_no in self.rating_bias:
            # 현 user와 다른 사용자간의 유사도 가져오기
            sim_scores = self.user_similarity[user_no]
            # 현 tag의 평점편차 가져오기
            tag_ratings = self.rating_bias[tag_no]
            # 현 tag에 대한 preference가 없는 사용자 표시
            no_rating = tag_ratings.isnull()
            # 현 사용자와 다른 사용자간 공통 평가 아이템 수 가져오기
            common_counts = self.counts[user_no]
            # 선호도가 없거나, SIG_LELEL이 기준 이하인 user 제거
            low_significance = common_counts < self.SIG_LEVEL
            none_rating_idx = tag_ratings[no_rating | low_significance].index
            tag_ratings = tag_ratings.drop(none_rating_idx)
            sim_scores = sim_scores.drop(none_rating_idx)
            # (2) Neighbor size가  지정되지 않았을 때
            if neighbor_size == 0:
                # 편차로 예측값 계산
                predicition = np.dot(sim_scores, tag_ratings) / sim_scores.sum()
                # 편차 예측값에 현 사용자의 평균 더하기
                predicition = predicition + self.rating_mean[user_no]
            # (3) Neighbor size가 지정된 경우
            else:
                # 해당 태그의 선호도가 있는 사용자가 최소 MIN_RATINGS 이상인 경우만 계산
                if len(sim_scores) > self.MIN_RATINGS:
                    # 지정된 neighbor size 값과 해당 태그의 선호도가 있는 총사용자 수 중 작은 것으로 결정
                    neighbor_size = min(neighbor_size, len(sim_scores))
                    # array로 바꾸기 (argsort를 사용하기 위함)
                    sim_scores = np.array(sim_scores)
                    tag_ratings = np.array(tag_ratings)
                    # 선호도를 순서대로 정렬
                    user_idx = np.argsort(sim_scores)
                    # 유사도와 preference를 neighbor size만큼 받기
                    sim_scores = sim_scores[user_idx][-neighbor_size:]
                    tag_ratings = tag_ratings[user_idx][-neighbor_size:]
                    # 편차로 예측치 계산
                    prediction = np.dot(sim_scores, tag_ratings) / sim_scores.sum()
                    # 예측값에 현 사용자의 평균 더하기
                    prediction = prediction + self.rating_mean[user_no]
                else:
                    prediction = self.rating_mean[user_no]
        else:
            prediction = self.rating_mean[user_no]
        return prediction

    # 유저의 선호도를 고려하지 않은 모든 유저의 선호도 평균을 내림차순으로 추천
    def recom_tag1(self, tag_mean, n_items, tags):
        tag_sort = tag_mean.sort_values(ascending=False)[:n_items]
        recom_tags = tags.loc[tag_sort.index]
        recommendations = recom_tags['tag']
        return recommendations

    def recom_tag(self, user_no, n_items, tags, neighbor_size=90):
        # 현 사용자가 평가한 태그 가져오기
        print(type(n_items))
        print(self.rating_bias)
        user_tag = self.rating_bias.loc[user_no].copy()

        for tagname in tqdm(self.rating_bias, desc="recom_tag"):
            # tag를 예상 선호도에 따라 정렬하여 태그 이름으로 리턴
            user_tag.loc[tagname] = self.CF_knn_bias_sig(user_no, tagname, neighbor_size)
            tag_sort = user_tag.sort_values(ascending=False)[:n_items]
            print(tag_sort)
            indexs = [i - 1 for i in tag_sort.index]
            print(tag_sort)
            print(indexs)
            recom_tags = tags.loc[indexs]
            recommendations = recom_tags['tag']

            return recommendations

    # RMSE 함수 생성
    def RMSE(self, y_true, y_pred):
        return np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2))

    # 모든 model의 RMSE를 계산해주는 함수
    def score(self, model, x_test, neighbor_size=0):
        id_pairs = zip(x_test['user_no'], x_test['tag_no'])
        y_pred = np.array([model(user, tagname, neighbor_size) for (user, tagname) in id_pairs])
        y_true = np.array(x_test['preference'])
        return self.RMSE(y_true, y_pred)

    # cosine similarity를 직접 구할 수 있는 함수
    def compute_cos_similarity(self, v1, v2):
        norm1 = np.sqrt(np.sum(np.square(v1)))
        norm2 = np.sqrt(np.sum(np.square(v2)))
        dot = np.dot(v1, v2)
        return dot / (norm1 * norm2)

    # 최적의 이웃의 수 정하기
    def set_best_neighbor_size(self, x_test):
        best_match = 6
        best_n_size = 0
        best_match_RMSE = 0
        for neighbor_size in tqdm([10, 20, 30, 40, 50, 60, 70, 80, 90, 100], desc="best_neighbor_size"):
            score = self.score(self.CF_knn_bias_sig, x_test, neighbor_size)
            if score < best_match:
                best_match = score
                best_n_size = neighbor_size
                best_match_RMSE = score
        self.best_neighbor_size = [best_n_size, best_match_RMSE]
