class ModelService:
    def __init__(self, model_dao):
        self.model_dao = model_dao

    def recommendation_update(self):
        try:
            self.model_dao.set_model()
            self.model_dao.update_tag_preferences()
            self.model_dao.set_recommend_images()
            return True
        except Exception as e:
            # Error 발생할 경우
            print("recommendation_update 실패")
            print(e)
            return False