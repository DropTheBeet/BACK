from sqlalchemy import text
from model.models import User

class UserDAO:
    def __init__(self, database):
        self.db = database;

    # 사용자 데이터 삽입 : 회원가입 시
    def insert_user(self, user):                # 입력값 : { "user_id" : "example_id", "user_pw" : "hashed_pw" }
        _user = User(user['user_id'], user['user_pw'])
        try:
            self.db.session.add(_user)
            self.db.session.commit()
        except Exception as e:
            print("INSERT_USER 실패 :", user)
            print(e)
            return False

        return True

    # 사용자 정보 조회 : 로그인 시 사용자의 번호 및 비밀번호를 조회
    def get_user_no_and_password(self, user_id):
        try:
            _user = User.query.filter_by(user_id=user_id)
        except Exception as e:
            print("GET_USER_NO_AND_PASSWORD 실패 :", user_id)
            print(e)
            return False;

        if _user is None:
            return None

        return _user[0].as_dict()




    #
    # def get_profile_picture(self, user_no):
    #     row = self.db.execute(text("""
    #         SELECT thum_url, img_no, reg_date
    #         FROM image
    #         WHERE user_no = :user_no
    #     """), {
    #         'user_no' : user_no
    #     }).fetchone()
    #
    #     return row['profile_picture'] if row else None
    #
    # def insert_follow(self, user_id, follow_id):
    #     return self.db.execute(text("""
    #         INSERT INTO users_follow_list (
    #             user_id,
    #             follow_user_id
    #         ) VALUES (
    #             :id,
    #             :follow
    #         )
    #     """), {
    #         'id'     : user_id,
    #         'follow' : follow_id
    #     }).rowcount
    #
    # def insert_unfollow(self, user_id, unfollow_id):
    #     return self.db.execute(text("""
    #         DELETE FROM users_follow_list
    #         WHERE user_id      = :id
    #         AND follow_user_id = :unfollow
    #     """), {
    #         'id'       : user_id,
    #         'unfollow' : unfollow_id
    #     }).rowcount
    #
    # def save_profile_picture(self, profile_pic_path, user_id):
    #     return self.db.execute(text("""
    #         UPDATE users
    #         SET profile_picture = :profile_pic_path
    #         WHERE id            = :user_id
    #     """), {
    #         'user_id'          : user_id,
    #         'profile_pic_path' : profile_pic_path
    #     }).rowcount
    #
    #
    #
    #
