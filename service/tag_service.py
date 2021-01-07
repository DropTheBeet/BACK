
class TagService:
    def __init__(self, tag_dao):
        self.tag_dao = tag_dao

    def get_tag_list_by_user(self, user_no):
        return self.tag_dao.get_tag_list_by_id(user_no)

    def get_tags_rating(self, user_no):
        return self.tag_dao.get_tags_rating(user_no)

    def get_public_tag_list(self):
        return self.tag_dao.get_tag_list_all()