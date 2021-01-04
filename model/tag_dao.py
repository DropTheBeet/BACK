from sqlalchemy import text

class TagDAO:
    def __init__(self, database):
        self.db = database

    def get_tag_list_by_id(self, user_no):
        user_tags = self.db.execute(text("""


        """), {
            'user_no': user_no
        }).fetchall()

        return [{
            'tag_no': user_tag[''],
            '대분류': user_tag[''],
            '중분류': user_tag[''],
        } for user_tag in user_tags]

    #대분류,중분류,태그


    def get_tag_list_all(self):
        public_tags = self.db.execute(text("""

        """)).fetchall()

        return [{
            'tag_no': public_tag[''],
            '대분류': public_tag[''],
            '중분류': public_tag[''],
        } for public_tag in public_tags]

    def get_tags_rating(self, user_no):
        tags_rating = self.db.execute(text("""

        """), {
            'user_no': user_no
        }).fetchall()


        return [{
            'tag_no': tag_rating['tag_no'],
            'rating': tag_rating['rating']
        } for tag_rating in tags_rating ]