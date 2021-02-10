class ModelService:
    def __init__(self, model_controller):
        self.model_controller = model_controller
        self.model_controller.set_input_data()
        self.model_controller.update_tag_preferences()
        self.model_controller.set_model()

    def recommendation_update(self):
        try:
            self.model_controller.set_input_data()
            self.model_controller.update_tag_preferences()
            self.model_controller.set_model()
            self.model_controller.set_recommend_images()
            return True
        except Exception as e:
            # Error 발생할 경우
            print("recommendation_update 실패")
            print(e)
            return False

    def set_recom_img(self, user_no):
        return self.model_controller.set_recom_img(user_no)