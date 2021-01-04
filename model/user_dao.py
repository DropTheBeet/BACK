from sqlalchemy import text

class UserDAO:
    def __init__(self, database):
        self.db = database

    def insert_user(self, user):
        return self.db.execute(text("""
            INSERT INTO user (
                user_id,
                user_pw
            ) VALUES (
                :name,
                :password
            )
        """), user).lastrowid

    def get_user_no_and_password(self, user_id):
        row = self.db.execute(text("""    
            SELECT
                user_no,
                user_pw
            FROM user
            WHERE user_id = :id
        """), {'id' : user_id}).fetchone()

        return {
            'user_no'         : row['user_no'],
            'hashed_password' : row['user_pw']
        } if row else None




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
