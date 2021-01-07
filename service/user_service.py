import os
import jwt
import bcrypt

from datetime import datetime, timedelta


class UserService:
    def __init__(self, user_dao, config):
        self.user_dao = user_dao
        self.config = config

    def create_new_user(self, new_user):
        new_user['user_pw'] = bcrypt.hashpw(
            new_user['user_pw'].encode('UTF-8'),
            bcrypt.gensalt()
        )

        new_user_id = self.user_dao.insert_user(new_user)

        return new_user_id

    def login(self, credential):
        user_id = credential['user_id']
        password = credential['user_pw']
        user_credential = self.user_dao.get_user_no_and_password(user_id)

        authorized = user_credential and bcrypt.checkpw(password.encode('UTF-8'),
                                                        user_credential['hashed_password'].encode('UTF-8'))

        return authorized

    def generate_access_token(self, user_no, user_id):
        payload = {
            'user_id': user_id,
            'user_no': user_no,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, self.config['JWT_SECRET_KEY'], 'HS256')

        return token.decode('UTF-8')


    def get_user_no_and_password(self, user_id):
        return self.user_dao.get_user_no_and_password(user_id)




    #

    #
    #
    # def save_profile_picture(self, picture, filename, user_id):
    #     self.s3.upload_fileobj(
    #         picture,
    #         self.config['S3_BUCKET'],
    #         filename
    #     )
    #
    #     image_url = f"{self.config['S3_BUCKET_URL']}{filename}"
    #
    #     return self.user_dao.save_profile_picture(image_url, user_id)

    #
    #
    # def follow(self, user_id, follow_id):
    #     return self.user_dao.insert_follow(user_id, follow_id)
    #
    # def unfollow(self, user_id, unfollow_id):
    #     return self.user_dao.insert_unfollow(user_id, unfollow_id)

